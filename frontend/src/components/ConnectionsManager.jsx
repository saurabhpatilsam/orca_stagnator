import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users, Plus, X, Trash2, Edit2, Check, Building2, Key, Shield, Server, Link2, Search
} from 'lucide-react';
import toast from 'react-hot-toast';
import { supabase } from '../config/supabase';

const ConnectionsManager = () => {
  const [users, setUsers] = useState([]);
  const [expandedUsers, setExpandedUsers] = useState({});
  const [showAddUser, setShowAddUser] = useState(false);
  const [showAddPlatform, setShowAddPlatform] = useState(null);
  const [editingPlatform, setEditingPlatform] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  const platformTypes = [
    { value: 'APEX', label: 'APEX', icon: Shield, color: 'bg-blue-500' },
    { value: 'MFF', label: 'MyForexFunds', icon: Building2, color: 'bg-green-500' },
    { value: 'TPT', label: 'TopTier', icon: Server, color: 'bg-purple-500' },
    { value: 'FTMO', label: 'FTMO', icon: Key, color: 'bg-orange-500' }
  ];

  // Fetch all data from Supabase
  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const { data: usersData, error: usersError } = await supabase
        .from('connection_users')
        .select(`
          *,
          platforms:connection_platforms(
            *,
            accounts:connection_accounts(*)
          )
        `)
        .order('created_at', { ascending: true });

      if (usersError) throw usersError;

      const formattedUsers = usersData.map(user => ({
        id: user.id,
        name: user.name,
        avatar: user.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=6366f1&color=fff`,
        platforms: user.platforms.map(platform => ({
          id: platform.id,
          type: platform.platform_type,
          name: platform.platform_name,
          status: platform.status,
          accounts: platform.accounts.map(account => ({
            id: account.id,
            name: account.account_name,
            balance: parseFloat(account.balance) || 0,
            status: account.status
          }))
        }))
      }));

      setUsers(formattedUsers);
    } catch (error) {
      console.error('Error fetching users:', error);
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  // Add user
  const handleAddUser = async (userName) => {
    try {
      const { data: { user: authUser } } = await supabase.auth.getUser();
      
      const { data, error } = await supabase
        .from('connection_users')
        .insert([{
          name: userName,
          avatar_url: `https://ui-avatars.com/api/?name=${encodeURIComponent(userName)}&background=6366f1&color=fff`,
          created_by: authUser?.id
        }])
        .select()
        .single();

      if (error) throw error;
      await fetchUsers();
      toast.success(`User ${userName} added successfully`);
      setShowAddUser(false);
    } catch (error) {
      console.error('Error adding user:', error);
      toast.error('Failed to add user');
    }
  };

  // Delete user
  const handleDeleteUser = async (userId, userName) => {
    if (window.confirm(`Are you sure you want to delete ${userName}? This will delete all platforms and accounts.`)) {
      try {
        const { error } = await supabase
          .from('connection_users')
          .delete()
          .eq('id', userId);

        if (error) throw error;
        await fetchUsers();
        toast.success(`User ${userName} deleted`);
      } catch (error) {
        console.error('Error deleting user:', error);
        toast.error('Failed to delete user');
      }
    }
  };

  // Add platform
  const handleAddPlatform = async (userId, platformData) => {
    try {
      const { data: platformInsert, error: platformError } = await supabase
        .from('connection_platforms')
        .insert([{
          user_id: userId,
          platform_type: platformData.type,
          platform_name: platformData.name,
          status: 'active'
        }])
        .select()
        .single();

      if (platformError) throw platformError;

      // Add accounts if provided
      if (platformData.accounts && platformData.accounts.length > 0) {
        const accountsToInsert = platformData.accounts.map(acc => ({
          platform_id: platformInsert.id,
          account_name: acc.name,
          balance: parseFloat(acc.balance) || 0,
          status: 'active'
        }));

        const { error: accountsError } = await supabase
          .from('connection_accounts')
          .insert(accountsToInsert);

        if (accountsError) throw accountsError;
      }

      await fetchUsers();
      toast.success(`Platform ${platformData.name} added`);
      setShowAddPlatform(null);
    } catch (error) {
      console.error('Error adding platform:', error);
      toast.error('Failed to add platform');
    }
  };

  // Update platform
  const handleUpdatePlatform = async (platformId, platformName) => {
    try {
      const { error } = await supabase
        .from('connection_platforms')
        .update({ platform_name: platformName })
        .eq('id', platformId);

      if (error) throw error;
      await fetchUsers();
      toast.success('Platform updated');
      setEditingPlatform(null);
    } catch (error) {
      console.error('Error updating platform:', error);
      toast.error('Failed to update platform');
    }
  };

  // Delete platform
  const handleDeletePlatform = async (userId, platformId, platformName) => {
    if (window.confirm(`Delete ${platformName}?`)) {
      try {
        const { error } = await supabase
          .from('connection_platforms')
          .delete()
          .eq('id', platformId);

        if (error) throw error;
        await fetchUsers();
        toast.success(`Platform ${platformName} deleted`);
      } catch (error) {
        console.error('Error deleting platform:', error);
        toast.error('Failed to delete platform');
      }
    }
  };

  // Delete account
  const handleDeleteAccount = async (accountId, accountName) => {
    if (window.confirm(`Delete account ${accountName}?`)) {
      try {
        const { error } = await supabase
          .from('connection_accounts')
          .delete()
          .eq('id', accountId);

        if (error) throw error;
        await fetchUsers();
        toast.success(`Account ${accountName} deleted`);
      } catch (error) {
        console.error('Error deleting account:', error);
        toast.error('Failed to delete account');
      }
    }
  };

  const toggleUser = (userId) => {
    setExpandedUsers(prev => ({ ...prev, [userId]: !prev[userId] }));
  };

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const StatusBadge = ({ status }) => {
    const styles = {
      active: 'bg-green-500/20 text-green-400 border-green-500/30',
      inactive: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
      pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
    };
    return (
      <span className={`px-2 py-0.5 text-xs rounded-full border ${styles[status]}`}>
        {status}
      </span>
    );
  };

  // Add User Modal - Simplified
  const AddUserModal = () => (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={() => setShowAddUser(false)}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-gray-800 rounded-xl p-6 w-96"
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="text-xl font-bold text-white mb-4">Add New User</h3>
        <form onSubmit={(e) => {
          e.preventDefault();
          const formData = new FormData(e.target);
          handleAddUser(formData.get('name'));
        }}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">User Name</label>
              <input
                type="text"
                name="name"
                required
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                placeholder="Enter user name"
              />
            </div>
          </div>
          <div className="flex gap-3 mt-6">
            <button
              type="button"
              onClick={() => setShowAddUser(false)}
              className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              Add User
            </button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  );

  // Add Platform Modal - Multi-step
  const AddPlatformModal = ({ userId }) => {
    const [accounts, setAccounts] = useState([{ name: '', balance: '' }]);
    const user = users.find(u => u.id === userId);

    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
        onClick={() => setShowAddPlatform(null)}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-gray-800 rounded-xl p-6 w-[500px] max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <h3 className="text-xl font-bold text-white mb-2">Add Platform & Accounts</h3>
          <p className="text-gray-400 text-sm mb-4">For {user.name}</p>

          <form onSubmit={(e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            handleAddPlatform(userId, {
              type: formData.get('type'),
              name: formData.get('name'),
              accounts: accounts.filter(acc => acc.name && acc.balance)
            });
          }}>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Platform Type</label>
                <select
                  name="type"
                  required
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                >
                  {platformTypes.map(platform => (
                    <option key={platform.value} value={platform.value}>
                      {platform.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">Platform Name</label>
                <input
                  type="text"
                  name="name"
                  required
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                  placeholder="e.g., APEX-136"
                />
              </div>

              <div className="border-t border-gray-700 pt-4">
                <div className="flex items-center justify-between mb-3">
                  <label className="text-sm text-gray-400">Accounts</label>
                  <button
                    type="button"
                    onClick={() => setAccounts([...accounts, { name: '', balance: '' }])}
                    className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1"
                  >
                    <Plus className="h-3 w-3" /> Add Account
                  </button>
                </div>
                
                {accounts.map((account, index) => (
                  <div key={index} className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={account.name}
                      onChange={(e) => {
                        const newAccounts = [...accounts];
                        newAccounts[index].name = e.target.value;
                        setAccounts(newAccounts);
                      }}
                      className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none text-sm"
                      placeholder="Account ID"
                    />
                    <input
                      type="number"
                      value={account.balance}
                      onChange={(e) => {
                        const newAccounts = [...accounts];
                        newAccounts[index].balance = e.target.value;
                        setAccounts(newAccounts);
                      }}
                      className="w-32 bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none text-sm"
                      placeholder="Balance"
                    />
                    {accounts.length > 1 && (
                      <button
                        type="button"
                        onClick={() => setAccounts(accounts.filter((_, i) => i !== index))}
                        className="p-2 text-red-400 hover:bg-gray-700 rounded-lg"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                type="button"
                onClick={() => setShowAddPlatform(null)}
                className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                Add Platform
              </button>
            </div>
          </form>
        </motion.div>
      </motion.div>
    );
  };

  if (loading) {
    return (
      <div className="h-full bg-gray-900 flex items-center justify-center">
        <div className="text-white text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p>Loading connections...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-gray-900 overflow-hidden flex flex-col">
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-semibold text-white flex items-center gap-2">
              <Link2 className="h-6 w-6 text-blue-400" />
              Connections Manager
            </h2>
            <p className="text-gray-400 text-sm mt-1">Manage users and their trading platform connections</p>
          </div>
          <button
            onClick={() => setShowAddUser(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            <Plus className="h-4 w-4" />
            Add User
          </button>
        </div>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search users..."
            className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="space-y-4">
          {filteredUsers.map(user => (
            <motion.div
              key={user.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden"
            >
              <div className="p-4 bg-gray-800/50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => toggleUser(user.id)}
                      className="text-gray-400 hover:text-white transition-colors"
                    >
                      {expandedUsers[user.id] ? (
                        <ChevronDown className="h-5 w-5" />
                      ) : (
                        <ChevronRight className="h-5 w-5" />
                      )}
                    </button>
                    <img
                      src={user.avatar}
                      alt={user.name}
                      className="h-10 w-10 rounded-full"
                    />
                    <div>
                      <h3 className="text-white font-semibold text-lg">{user.name}</h3>
                      <p className="text-gray-400 text-sm">{user.platforms.length} platforms</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setShowAddPlatform(user.id)}
                      className="p-2 text-blue-400 hover:bg-gray-700 rounded-lg transition-colors"
                      title="Add Platform"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteUser(user.id, user.name)}
                      className="p-2 text-red-400 hover:bg-gray-700 rounded-lg transition-colors"
                      title="Delete User"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>

              <AnimatePresence>
                {expandedUsers[user.id] && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="border-t border-gray-700"
                  >
                    <div className="p-4">
                      {user.platforms.length === 0 ? (
                        <div className="text-center py-8">
                          <Server className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                          <p className="text-gray-500">No platforms added yet</p>
                          <button
                            onClick={() => setShowAddPlatform(user.id)}
                            className="mt-3 text-blue-400 hover:text-blue-300 text-sm"
                          >
                            Add first platform
                          </button>
                        </div>
                      ) : (
                        <div className="grid grid-cols-3 gap-4">
                          {user.platforms.map(platform => {
                            const PlatformIcon = platformTypes.find(p => p.value === platform.type)?.icon || Building2;
                            const platformColor = platformTypes.find(p => p.value === platform.type)?.color || 'bg-gray-500';

                            return (
                              <div key={platform.id} className="bg-gray-900 rounded-lg border border-gray-700 p-4">
                                <div className="flex items-start justify-between mb-3">
                                  <div className="flex items-center gap-2">
                                    <div className={`p-2 ${platformColor} rounded-lg`}>
                                      <PlatformIcon className="h-5 w-5 text-white" />
                                    </div>
                                    <div>
                                      {editingPlatform === platform.id ? (
                                        <input
                                          type="text"
                                          defaultValue={platform.name}
                                          onBlur={(e) => handleUpdatePlatform(platform.id, e.target.value)}
                                          onKeyDown={(e) => {
                                            if (e.key === 'Enter') {
                                              handleUpdatePlatform(platform.id, e.target.value);
                                            }
                                          }}
                                          className="bg-gray-800 border border-gray-600 rounded px-2 py-1 text-white text-sm focus:border-blue-500 focus:outline-none"
                                          autoFocus
                                        />
                                      ) : (
                                        <div>
                                          <h4 className="text-white font-medium text-sm">{platform.name}</h4>
                                          <p className="text-gray-400 text-xs">{platform.type}</p>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                  <div className="flex gap-1">
                                    <button
                                      onClick={() => setEditingPlatform(platform.id)}
                                      className="p-1 text-gray-400 hover:text-blue-400 hover:bg-gray-800 rounded transition-colors"
                                      title="Edit"
                                    >
                                      <Edit2 className="h-3 w-3" />
                                    </button>
                                    <button
                                      onClick={() => handleDeletePlatform(user.id, platform.id, platform.name)}
                                      className="p-1 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded transition-colors"
                                      title="Delete"
                                    >
                                      <Trash2 className="h-3 w-3" />
                                    </button>
                                  </div>
                                </div>

                                <StatusBadge status={platform.status} />

                                <div className="mt-3 space-y-2">
                                  <div className="flex items-center justify-between">
                                    <span className="text-gray-400 text-xs">Accounts ({platform.accounts.length})</span>
                                  </div>
                                  {platform.accounts.map(account => (
                                    <div
                                      key={account.id}
                                      className="flex items-center justify-between px-2 py-1.5 bg-gray-800 rounded text-xs"
                                    >
                                      <div>
                                        <span className="text-white font-mono block">{account.name}</span>
                                        <span className="text-gray-400">${account.balance.toLocaleString()}</span>
                                      </div>
                                      <button
                                        onClick={() => handleDeleteAccount(account.id, account.name)}
                                        className="p-1 text-red-400 hover:bg-gray-700 rounded"
                                      >
                                        <X className="h-3 w-3" />
                                      </button>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}

          {filteredUsers.length === 0 && (
            <div className="text-center py-16">
              <Users className="h-16 w-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 text-lg mb-2">No users found</p>
              <button
                onClick={() => setShowAddUser(true)}
                className="text-blue-400 hover:text-blue-300"
              >
                Add your first user
              </button>
            </div>
          )}
        </div>
      </div>

      <AnimatePresence>
        {showAddUser && <AddUserModal />}
        {showAddPlatform && <AddPlatformModal userId={showAddPlatform} />}
      </AnimatePresence>
    </div>
  );
};

export default ConnectionsManager;
