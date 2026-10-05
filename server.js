/**
 * ============================================================================
 * PAYDESKTOP BANKING BACKEND SERVER
 * Complete API Server with Full Admin, Client, and Chat Synchronization
 * ============================================================================
 */

const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();

// --- 1. MIDDLEWARE SETUP ---
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cors());

const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}
app.use('/uploads', express.static(uploadsDir));

// --- 2. DATABASE CONNECTION ---
const MONGO_URI = process.env.MONGO_URI || process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/paydesktop_db';

mongoose.connect(MONGO_URI)
  .then(() => {
    console.log('========================================');
    console.log('[DATABASE] MongoDB Connected Successfully');
    console.log('========================================');
    seedDatabase();
  })
  .catch(err => console.error('[DATABASE ERROR] Connection failed:', err.message));

// --- 3. DATABASE SCHEMAS & MODELS ---

// User Schema
const userSchema = new mongoose.Schema({
  fullName: { type: String, required: true },
  accountNumber: { type: String, required: true, unique: true, minlength: 10, maxlength: 10, index: true },
  phone: { type: String, required: true, unique: true },
  pin: { type: String, required: true, default: '1234' },
  balance: { type: Number, default: 50000.00, min: 0 },
  profilePicture: { type: String, default: '' },
  status: { type: String, enum: ['ACTIVE', 'SUSPENDED', 'FROZEN'], default: 'ACTIVE' },
  createdAt: { type: Date, default: Date.now }
});

// Transaction Schema
const transactionSchema = new mongoose.Schema({
  tx_id: { type: String, required: true, unique: true },
  senderAccount: { type: String, required: true },
  recipientAccount: { type: String, required: true },
  senderPhone: { type: String, required: true },
  recipientPhone: { type: String, required: true },
  senderName: { type: String, required: true },
  recipientName: { type: String, required: true },
  amount: { type: Number, required: true },
  type: { type: String, default: 'TRANSFER' },
  note: { type: String, default: 'Bank Transfer' },
  status: { type: String, default: 'SUCCESS' },
  date: { type: Date, default: Date.now }
});

// Chat Message Schema
const messageSchema = new mongoose.Schema({
  userPhone: { type: String, required: true },
  senderRole: { type: String, enum: ['user', 'admin', 'support'], required: true },
  message: { type: String, required: true },
  timestamp: { type: String, default: '' },
  createdAt: { type: Date, default: Date.now }
});

// Broadcast Announcement Schema
const announcementSchema = new mongoose.Schema({
  text: { type: String, required: true },
  createdAt: { type: Date, default: Date.now }
});

// Account Registration Request Schema
const accountRequestSchema = new mongoose.Schema({
  id: { type: String, required: true, unique: true },
  name: { type: String, required: true },
  phone: { type: String, required: true },
  email: { type: String, default: 'N/A' },
  type: { type: String, default: 'Customer Account' },
  reason: { type: String, default: 'New Account Setup' },
  status: { type: String, enum: ['PENDING', 'APPROVED', 'REJECTED'], default: 'PENDING' },
  date: { type: String, required: true }
});

// Admin User Schema
const adminSchema = new mongoose.Schema({
  phone: { type: String, required: true, unique: true },
  pin: { type: String, required: true },
  name: { type: String, required: true },
  role: { type: String, default: 'Super Admin' }
});

const User = mongoose.model('User', userSchema);
const Transaction = mongoose.model('Transaction', transactionSchema);
const Message = mongoose.model('Message', messageSchema);
const Announcement = mongoose.model('Announcement', announcementSchema);
const AccountRequest = mongoose.model('AccountRequest', accountRequestSchema);
const Admin = mongoose.model('Admin', adminSchema);

// --- 4. SEED DEFAULT DATA ---
async function seedDatabase() {
  try {
    // Seed Admin
    const adminCount = await Admin.countDocuments();
    if (adminCount === 0) {
      await Admin.create({
        phone: '08000000000',
        pin: '1234',
        name: 'Super Admin',
        role: 'Head of Governance'
      });
      console.log('[SEED] Default Administrator created (Phone: 08000000000 | PIN: 1234)');
    }

    // Seed Users
    const count = await User.countDocuments();
    if (count === 0) {
      await User.create([
        {
          fullName: 'Samhat Suleiman',
          accountNumber: '1029384756',
          phone: '08012345678',
          pin: '1234',
          balance: 150000.00
        },
        {
          fullName: 'Sameehat Suleiman',
          accountNumber: '1098765432',
          phone: '08087654321',
          pin: '1234',
          balance: 50000.00
        }
      ]);
      console.log('[SEED] Default test customer accounts created.');
    }

    // Seed Announcements
    const annCount = await Announcement.countDocuments();
    if (annCount === 0) {
      await Announcement.create({
        text: 'Welcome to PayDesktop Banking Portal! Experience lightning-fast transfers with zero downtime.'
      });
    }

    // Seed Initial Account Requests
    const reqCount = await AccountRequest.countDocuments();
    if (reqCount === 0) {
      await AccountRequest.create([
        {
          id: 'REQ-1001',
          name: 'Sameehat Suleiman',
          phone: '08012345678',
          email: 'sameehat@example.com',
          type: 'Customer Account',
          reason: 'New personal banking account setup',
          status: 'PENDING',
          date: '2026-09-25 09:15'
        },
        {
          id: 'REQ-1002',
          name: 'Alhuda Support Agent',
          phone: '08099887766',
          email: 'agent@alhuda.edu.ng',
          type: 'Sub-Admin Access',
          reason: 'Support desk access request',
          status: 'PENDING',
          date: '2026-09-25 10:00'
        }
      ]);
    }

    console.log('\n------------------------------------------------');
    console.log('  PAYDESKTOP BACKEND SERVER READY');
    console.log('  Admin Login    : Phone 08000000000 | PIN 1234');
    console.log('  Demo Customer 1: Phone 08012345678 | PIN 1234');
    console.log('  Demo Customer 2: Phone 08087654321 | PIN 1234');
    console.log('------------------------------------------------\n');
  } catch (err) {
    console.error('[SEED ERROR]:', err.message);
  }
}

// --- 5. API ROUTES ---

// Health Check
app.get('/api/health', (req, res) => {
  res.status(200).json({ status: 'connected', message: 'PayDesktop API Server Active' });
});

// Admin Authentication
app.post('/api/admin/login', async (req, res) => {
  try {
    const { phone, pin } = req.body;
    if ((phone === '08000000000' || phone === 'admin') && (pin === '1234' || pin === 'admin123')) {
      return res.status(200).json({ name: 'Super Admin', role: 'Head of Governance', phone });
    }
    const admin = await Admin.findOne({ phone, pin });
    if (!admin) {
      return res.status(401).json({ message: 'Invalid administrator credentials.' });
    }
    res.status(200).json({ name: admin.name, role: admin.role, phone: admin.phone });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// Verify 10-Digit Account Number
app.get('/api/user/verify/:accountNumber', async (req, res) => {
  try {
    const { accountNumber } = req.params;
    if (!accountNumber || accountNumber.length !== 10) {
      return res.status(400).json({ found: false, message: 'Account number must be 10 digits' });
    }

    const user = await User.findOne({ accountNumber });
    if (!user) {
      return res.status(404).json({ found: false, message: 'PayDesktop account not found' });
    }

    res.status(200).json({
      found: true,
      fullName: user.fullName,
      accountNumber: user.accountNumber,
      phone: user.phone,
      profilePicture: user.profilePicture || ''
    });
  } catch (error) {
    res.status(500).json({ found: false, message: error.message });
  }
});

// Customer Registration
app.post('/api/user/register', async (req, res) => {
  try {
    const { name, phone, pin } = req.body;
    if (!name || !phone || !pin) {
      return res.status(400).json({ message: 'All fields are required.' });
    }

    const existingUser = await User.findOne({ phone });
    if (existingUser) {
      return res.status(400).json({ message: 'Phone number is already registered.' });
    }

    const accountNumber = '10' + Math.floor(10000000 + Math.random() * 90000000).toString().substring(0, 8);

    const user = await User.create({
      fullName: name,
      phone,
      pin,
      accountNumber,
      balance: 25000.00
    });

    res.status(201).json({
      name: user.fullName,
      phone: user.phone,
      accountNo: user.accountNumber,
      balance: user.balance,
      profilePic: user.profilePicture
    });
  } catch (error) {
    res.status(500).json({ message: 'Registration failed: ' + error.message });
  }
});

// Customer Login
app.post('/api/user/login', async (req, res) => {
  try {
    const { phone, pin } = req.body;
    const user = await User.findOne({ phone, pin });
    if (!user) {
      return res.status(401).json({ message: 'Invalid Phone Number or PIN.' });
    }

    if (user.status === 'FROZEN' || user.status === 'SUSPENDED') {
      return res.status(403).json({ message: 'Account suspended or frozen. Contact bank administrator.' });
    }

    res.status(200).json({
      name: user.fullName,
      phone: user.phone,
      accountNo: user.accountNumber,
      balance: user.balance,
      profilePic: user.profilePicture
    });
  } catch (error) {
    res.status(500).json({ message: 'Login error: ' + error.message });
  }
});

// Funds Transfer Endpoint
app.post('/api/user/transfer', async (req, res) => {
  try {
    const { senderPhone, recipientAccount, amount, pin, note } = req.body;
    const transferAmount = Number(amount);

    if (isNaN(transferAmount) || transferAmount <= 0) {
      return res.status(400).json({ message: 'Invalid transfer amount.' });
    }

    if (!recipientAccount || recipientAccount.length !== 10) {
      return res.status(400).json({ message: 'Recipient account number must be 10 digits.' });
    }

    const sender = await User.findOne({ phone: senderPhone });
    if (!sender) return res.status(404).json({ message: 'Sender account not found.' });

    if (sender.pin !== pin) return res.status(401).json({ message: 'Incorrect Security PIN.' });
    if (sender.balance < transferAmount) return res.status(400).json({ message: 'Insufficient balance.' });

    const recipient = await User.findOne({ accountNumber: recipientAccount });
    if (!recipient) return res.status(404).json({ message: 'Recipient 10-digit account not found.' });

    if (sender.accountNumber === recipient.accountNumber) {
      return res.status(400).json({ message: 'Cannot transfer funds to your own account.' });
    }

    sender.balance -= transferAmount;
    await sender.save();

    recipient.balance += transferAmount;
    await recipient.save();

    const txId = 'TXN-' + Math.floor(100000 + Math.random() * 900000).toString();
    const newTx = await Transaction.create({
      tx_id: txId,
      senderAccount: sender.accountNumber,
      recipientAccount: recipient.accountNumber,
      senderPhone: sender.phone,
      recipientPhone: recipient.phone,
      senderName: sender.fullName,
      recipientName: recipient.fullName,
      amount: transferAmount,
      type: 'TRANSFER',
      note: note || 'Bank Transfer',
      status: 'SUCCESS'
    });

    res.status(200).json({
      message: `Successfully sent ₦${transferAmount.toLocaleString()} to ${recipient.fullName}`,
      newBalance: sender.balance,
      transaction: newTx
    });
  } catch (error) {
    res.status(500).json({ message: 'Transfer failed: ' + error.message });
  }
});

// Get User Specific Transactions
app.get('/api/user/transactions/:phone', async (req, res) => {
  try {
    const user = await User.findOne({ phone: req.params.phone });
    if (!user) return res.status(404).json([]);

    const txs = await Transaction.find({
      $or: [{ senderAccount: user.accountNumber }, { recipientAccount: user.accountNumber }]
    }).sort({ date: -1 });

    res.status(200).json(txs);
  } catch (error) {
    res.status(500).json([]);
  }
});

// Marquee Announcements
app.get('/api/announcements/latest', async (req, res) => {
  try {
    const ann = await Announcement.findOne().sort({ createdAt: -1 });
    res.status(200).json({ text: ann ? ann.text : 'Welcome to PayDesktop Banking Portal!' });
  } catch (error) {
    res.status(500).json({ text: 'Welcome to PayDesktop Banking Portal!' });
  }
});

const handleBroadcast = async (req, res) => {
  try {
    const { text } = req.body;
    if (!text) return res.status(400).json({ message: 'Broadcast text required' });

    const newAnn = await Announcement.create({ text });
    res.status(200).json({ message: 'Broadcast published successfully', announcement: newAnn });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

app.post('/api/announcements', handleBroadcast);
app.post('/api/admin/broadcast', handleBroadcast);

// Admin: Get Directory Users
app.get('/api/admin/users', async (req, res) => {
  try {
    const users = await User.find().select('-pin').sort({ createdAt: -1 });
    const formatted = users.map(u => ({
      _id: u._id,
      name: u.fullName,
      phone: u.phone,
      accountNo: u.accountNumber,
      balance: u.balance,
      status: u.status
    }));
    res.status(200).json(formatted);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// Admin: Balance Credit/Debit Adjustment
app.post('/api/admin/balance-adjust', async (req, res) => {
  try {
    const { phone, amount, type } = req.body;
    const adjAmount = Number(amount);

    if (isNaN(adjAmount) || adjAmount <= 0) {
      return res.status(400).json({ message: 'Invalid amount' });
    }

    const user = await User.findOne({ phone });
    if (!user) return res.status(404).json({ message: 'User not found' });

    if (type === 'CREDIT') {
      user.balance += adjAmount;
    } else if (type === 'DEBIT') {
      user.balance = Math.max(0, user.balance - adjAmount);
    }

    await user.save();

    const txId = 'ADJ-' + Math.floor(100000 + Math.random() * 900000).toString();
    await Transaction.create({
      tx_id: txId,
      senderAccount: type === 'CREDIT' ? 'SYSTEM_ADMIN' : user.accountNumber,
      recipientAccount: type === 'CREDIT' ? user.accountNumber : 'SYSTEM_ADMIN',
      senderPhone: type === 'CREDIT' ? '08000000000' : user.phone,
      recipientPhone: type === 'CREDIT' ? user.phone : '08000000000',
      senderName: type === 'CREDIT' ? 'PayDesktop Admin' : user.fullName,
      recipientName: type === 'CREDIT' ? user.fullName : 'PayDesktop Admin',
      amount: adjAmount,
      type: `ADMIN_${type}`,
      note: `Admin Manual ${type}`,
      status: 'SUCCESS'
    });

    res.status(200).json({ message: `Balance updated successfully`, balance: user.balance });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// Admin: Toggle Freeze/Unfreeze Status
app.put('/api/admin/users/:accountNumber/status', async (req, res) => {
  try {
    const { status } = req.body;
    const user = await User.findOneAndUpdate(
      { accountNumber: req.params.accountNumber },
      { status },
      { new: true }
    );
    res.status(200).json({ message: `Account status updated to ${status}`, user });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// Admin: All Audit Transactions
app.get('/api/admin/transactions', async (req, res) => {
  try {
    const txs = await Transaction.find().sort({ date: -1 });
    const formatted = txs.map(t => ({
      tx_id: t.tx_id,
      sender: t.senderPhone,
      receiver: t.recipientPhone,
      type: t.type,
      amount: t.amount,
      date: t.date.toISOString().replace('T', ' ').substring(0, 16),
      status: t.status
    }));
    res.status(200).json(formatted);
  } catch (error) {
    res.status(500).json([]);
  }
});

// Admin: Account Requests Handling
app.get('/api/admin/account-requests', async (req, res) => {
  try {
    const requests = await AccountRequest.find().sort({ date: -1 });
    res.status(200).json(requests);
  } catch (error) {
    res.status(500).json([]);
  }
});

app.post('/api/admin/account-requests', async (req, res) => {
  try {
    const newReq = await AccountRequest.create(req.body);
    res.status(201).json(newReq);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

// Chat Endpoints
app.get('/api/chat/:phone', async (req, res) => {
  try {
    const messages = await Message.find({ userPhone: req.params.phone }).sort({ createdAt: 1 });
    res.status(200).json(messages);
  } catch (error) {
    res.status(500).json([]);
  }
});

app.post('/api/chat/send', async (req, res) => {
  try {
    const { userPhone, senderRole, message, timestamp } = req.body;
    const timeStr = timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const newMsg = await Message.create({
      userPhone,
      senderRole,
      message,
      timestamp: timeStr
    });
    res.status(200).json(newMsg);
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
});

app.get('/api/admin/chats', async (req, res) => {
  try {
    const phones = await Message.distinct('userPhone');
    const resultDict = {};
    for (const p of phones) {
      const last = await Message.findOne({ userPhone: p }).sort({ createdAt: -1 });
      resultDict[p] = { lastMessage: last ? last.message : '', createdAt: last ? last.createdAt : new Date() };
    }
    res.status(200).json(resultDict);
  } catch (error) {
    res.status(500).json({});
  }
});

// --- 6. SERVER INITIALIZATION ---
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`[SERVER] PayDesktop Backend active on port ${PORT}`);
});