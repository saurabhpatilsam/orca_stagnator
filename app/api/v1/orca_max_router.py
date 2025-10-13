import datetime
import json
from typing import Optional, List, Union, Dict
from fastapi import APIRouter, HTTPException, Body
from fastapi import UploadFile, File, Form
from starlette.responses import JSONResponse
from app.api.v1.endpoints.max_backtest import run_max_backtest_logic
from app.api.v1.endpoints.max_live import run_orca_system
from app.services.orca_max.helpers.enums import ENVIRONMENT,TeamWay, PointType, Contract
from app.services.orca_max.schemas import AccountConfig
from app.services.orca_max_backtesting.helper import read_bytes_cleaned

max_router = APIRouter(prefix="/run-bot")


@max_router.post("/max-backtest")
async def run_bot_backtesting(
    accountName: str = Form(...),
    mode: str = Form(...),
    contract: str = Form(...),
    maxMode: str = Form(...),
    point_key: str = Form(...),
    exit_strategy_key: str = Form(...),
    notes: Optional[str] = Form(None),
    dateFrom: Optional[str] = Form(None),
    dateTo: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    try:
        payload = await run_max_backtest_logic(
            account_name=accountName,
            mode=mode,
            contract=contract,
            max_mode_value=maxMode,
            point_key=point_key,
            exit_strategy_key=exit_strategy_key,
            notes=notes,
            date_from=dateFrom,
            date_to=dateTo,
            file=file,
        )
        return JSONResponse(content=payload, status_code=200)

    except HTTPException:
        # Re-raise FastAPI-native errors as-is
        raise
    except Exception as e:
        # Fall-through for anything unexpected
        raise HTTPException(status_code=500, detail=str(e))

@max_router.post("/max")
async def run_bot_max(
    accountName: str = Form("APEX_136189"),
    contract: Union[Contract] = Form(),
    maxMode: Optional[str] = Form(...),
    trading_mode: Union[TeamWay] = Form(),
    trading_side: Union[PointType] = Form(),
    point_strategy_key: str = Form("15_7_5_2"),
    exit_strategy_key: str = Form("15_15"),
    dateFrom: Optional[datetime.datetime] = Form(),
    dateTo: Optional[datetime.datetime] = Form(),
    # file: Optional[UploadFile] = File(None),
    # parse these from form too for consistency
    quantity: int = Form(1),
    environment: Optional[ENVIRONMENT] = Form(),
    # accept JSON string; client sends accounts_ids='[{"id": "...", ...}]'
    # [{"tv_id"="D18156705", "ta_id"="PAAPEX1361890000008"}]
    accounts_ids: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):

    try:
        file = None
        # 1) File path: parse and run
        if file:
            contents = await file.read()
            if contents is None or len(contents) == 0:
                raise HTTPException(status_code=400, detail="Uploaded file is empty.")

            # Parse uploaded dataset
            data, all_data = read_bytes_cleaned(contents, rows=-1)

        parsed_accounts: Optional[List[AccountConfig]] = None
        if accounts_ids and accounts_ids != [""]:
            parsed = json.loads(accounts_ids)
            # Pydantic-validate each entry
            parsed_accounts = [AccountConfig(**item) for item in parsed]

        run_config = {
            "main_account": accountName,
            "instrument_name": contract.value,
            "way": TeamWay(trading_mode),
            # "max_mode_value": maxMode,
            "point_type": PointType(trading_side),
            "point_strategy_key": point_strategy_key,
            "exit_strategy_key": exit_strategy_key,
            "quantity": quantity,
            "environment": (
                environment.value
                if isinstance(environment, ENVIRONMENT)
                else environment
            ),
            "price_file": file,  # whatever your system expects here
            "start_time": dateFrom,
            "end_time": dateTo,
            "accounts_ids": parsed_accounts,
            "notes": notes,
        }

        # asyncio.create_task(asyncio.to_thread(run_orca_system, run_config))
        # If run_orca_system is CPU/blocking, avoid blocking the event loop:
        result = await run_orca_system(run_config)
        return JSONResponse(content=result, status_code=200)
    except HTTPException:
        raise
    except Exception as e:
        raise e
        raise HTTPException(status_code=500, detail="Internal server error")
