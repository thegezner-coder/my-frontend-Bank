const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const crypto = require('crypto');

const app = express();
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));
app.set('view engine', 'ejs');
app.use(cors());

// MongoDB Connection (Fixed for Railway & Local)
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/paydesktop_bank';
mongoose.connect(MONGO_URI)
.then(async () => {
    console.log('Connected to MongoDB successfully');
    await seedAdmins();
})
.catch(err => console.error('MongoDB connection error:', err));

// ==========================================
// SCHEMAS & MODELS
// ==========================================
const userSchema = new mongoose.Schema({
    name: { type: String, required: true },
    phone: { type: String, required: true, unique: true },
    email: { type: String },
    pin: { type: String, required: true },
    accountNo: { type: String, required: true, unique: true },
    accountType: { type: String, default: 'Savings' },
    balance: { type: Number, default: 0.0 },
    kycTier: { type: String, enum: ['Tier 1', 'Tier 2', 'Tier 3'], default: 'Tier 1' },
    status: { type: String, enum: ['PENDING', 'ACTIVE', 'FROZEN', 'REJECTED'], default: 'PENDING' },
    cardStatus: { type: String, enum: ['NOT_REQUESTED', 'PENDING', 'ASSIGNED', 'ACTIVE'], default: 'NOT_REQUESTED' },
    cardDetails: {
        cardNumber: { type: String, default: '' },
        expiry: { type: String, default: '' },
        cvv: { type: String, default: '' }
    },
    profilePic: { type: String, default: '' },
    lastLogin: { type: String, default: 'Never' },
    createdAt: { type: Date, default: Date.now }
});
const User = mongoose.model('User', userSchema);

const beneficiarySchema = new mongoose.Schema({
    userPhone: { type: String, required: true },
    name: { type: String, required: true },
    accountNumber: { type: String, required: true },
    bankName: { type: String, default: 'PayDesktop Bank' }
});
const Beneficiary = mongoose.model('Beneficiary', beneficiarySchema);

const adminSchema = new mongoose.Schema({
    name: { type: String, required: true },
    phone: { type: String, required: true, unique: true },
    pin: { type: String, required: true },
    role: { type: String, enum: ['super_admin', 'admin'], default: 'admin' },
    lastLogin: { type: String, default: 'Never' }
});
const Admin = mongoose.model('Admin', adminSchema);

const transactionSchema = new mongoose.Schema({
    tx_id: { type: String, required: true, unique: true },
    senderPhone: { type: String },
    senderName: { type: String },
    senderAccount: { type: String }, 
    recipientPhone: { type: String },
    recipientName: { type: String },
    recipientAccount: { type: String },
    recipientBank: { type: String, default: 'PayDesktop Bank' },
    amount: { type: Number, required: true },
    type: { type: String, required: true },
    note: { type: String },
    date: { type: Date, default: Date.now }
});
const Transaction = mongoose.model('Transaction', transactionSchema);

const chatSchema = new mongoose.Schema({
    userPhone: { type: String, required: true },
    senderRole: { type: String, enum: ['user', 'admin', 'super_admin'], required: true },
    message: { type: String, required: true },
    timestamp: { type: String, default: () => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) },
    date: { type: Date, default: Date.now }
});
const Chat = mongoose.model('Chat', chatSchema);

const broadcastSchema = new mongoose.Schema({
    text: { type: String, required: true },
    active: { type: Boolean, default: true },
    date: { type: Date, default: Date.now }
});
const Broadcast = mongoose.model('Broadcast', broadcastSchema);

const adminRequestSchema = new mongoose.Schema({
    adminPhone: { type: String, required: true },
    adminName: { type: String, required: true },
    actionType: { type: String, required: true },
    targetAccountNo: { type: String, required: true },
    targetName: { type: String },
    status: { type: String, enum: ['PENDING', 'APPROVED', 'REJECTED'], default: 'PENDING' },
    date: { type: Date, default: Date.now }
});
const AdminRequest = mongoose.model('AdminRequest', adminRequestSchema);

// SHAREABLE TRANSFER LINKS SCHEMA
const transferLinkSchema = new mongoose.Schema({
    token: { type: String, required: true, unique: true },
    recipientName: { type: String, required: true },
    bankName: { type: String, required: true },
    accountNumber: { type: String, required: true },
    amount: { type: Number, required: true },
    status: { type: String, default: 'PENDING' },
    createdAt: { type: Date, default: Date.now }
});
const TransferLink = mongoose.model('TransferLink', transferLinkSchema);

async function seedAdmins() {
    const count = await Admin.countDocuments();
    if (count === 0) {
        await Admin.create({ name: 'Super Admin Mujahid', phone: '08000000000', pin: '1234', role: 'super_admin' });
        await Admin.create({ name: 'Branch Admin', phone: '08011111111', pin: '1234', role: 'admin' });
        console.log('Default Admins seeded successfully.');
    }
}

function getKycLimits(tier) {
    if (tier === 'Tier 1') return { maxBalance: 300000, dailyTransfer: 290000 };
    if (tier === 'Tier 2') return { maxBalance: 500000, dailyTransfer: 490000 };
    if (tier === 'Tier 3') return { maxBalance: Infinity, dailyTransfer: 5000000 };
    return { maxBalance: 300000, dailyTransfer: 290000 };
}

// ==========================================
// ADMIN API ROUTES
// ==========================================
app.post('/api/admin/login', async (req, res) => {
    try {
        const { phone, pin } = req.body;
        const admin = await Admin.findOne({ phone, pin });
        if (!admin) return res.status(401).json({ message: 'Invalid admin credentials.' });
        admin.lastLogin = new Date().toLocaleString();
        await admin.save();
        res.json(admin);
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/admin/register', async (req, res) => {
    try {
        const { name, phone, pin, role } = req.body;
        const existing = await Admin.findOne({ phone });
        if (existing) return res.status(400).json({ message: 'Admin phone already registered.' });
        await Admin.create({ name, phone, pin, role: role || 'admin' });
        res.status(201).json({ message: 'Admin registered successfully!' });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.get('/api/admin/pending-users', async (req, res) => {
    try {
        const pending = await User.find({ status: 'PENDING' });
        res.json(pending);
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/admin/user/approve', async (req, res) => {
    try {
        const { accountNumber } = req.body;
        const user = await User.findOneAndUpdate({ accountNo: accountNumber }, { status: 'ACTIVE' }, { new: true });
        if (!user) return res.status(404).json({ message: 'User not found.' });
        res.json({ message: `Account ${accountNumber} approved successfully!` });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/admin/user/reject', async (req, res) => {
    try {
        const { accountNumber } = req.body;
        const user = await User.findOneAndUpdate({ accountNo: accountNumber }, { status: 'REJECTED' }, { new: true });
        if (!user) return res.status(404).json({ message: 'User not found.' });
        res.json({ message: `Account ${accountNumber} rejected.` });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.get('/api/admin/users', async (req, res) => {
    try {
        const users = await User.find();
        res.json(users);
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/admin/balance-adjust', async (req, res) => {
    try {
        const { phone, amount, type } = req.body;
        const user = await User.findOne({ phone });
        if (!user) return res.status(404).json({ message: 'User not found.' });

        const limits = getKycLimits(user.kycTier);
        if (type === 'CREDIT') {
            if (user.balance + Number(amount) > limits.maxBalance) {
                return res.status(400).json({ message: `Credit exceeds KYC ${user.kycTier} max balance limit.` });
            }
            user.balance += Number(amount);
        } else if (type === 'DEBIT') {
            if (user.balance < amount) return res.status(400).json({ message: 'Insufficient balance for debit.' });
            user.balance -= Number(amount);
        }
        await user.save();
        res.json({ message: `Successfully ${type.toLowerCase()}ed ₦${amount}`, newBalance: user.balance });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.put('/api/admin/users/:accountNo/status', async (req, res) => {
    try {
        const { status } = req.body;
        const user = await User.findOneAndUpdate({ accountNo: req.params.accountNo }, { status }, { new: true });
        if (!user) return res.status(404).json({ message: 'User not found.' });
        res.json({ message: `Status updated to ${status}` });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.put('/api/admin/users/:accountNo/edit', async (req, res) => {
    try {
        const { name, email, phone } = req.body;
        const updateData = {};
        if (name) updateData.name = name;
        if (email) updateData.email = email;
        if (phone) updateData.phone = phone;

        const user = await User.findOneAndUpdate({ accountNo: req.params.accountNo }, updateData, { new: true });
        if (!user) return res.status(404).json({ message: 'User not found.' });
        res.json({ message: 'Customer profile updated successfully', user });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/admin/assign-card', async (req, res) => {
    try {
        const { accountNo } = req.body;
        const user = await User.findOne({ accountNo });
        if (!user) return res.status(404).json({ message: 'Customer not found.' });

        const randomCard = '5399' + Math.floor(100000000000 + Math.random() * 900000000000);
        const cvv = Math.floor(100 + Math.random() * 900).toString();
        user.cardStatus = 'ASSIGNED';
        user.cardDetails = { cardNumber: randomCard, expiry: '12/29', cvv };
        await user.save();

        res.json({ message: `ATM Card successfully assigned to ${user.name}!`, card: user.cardDetails });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.delete('/api/admin/user/:accountNo', async (req, res) => {
    try {
        await User.findOneAndDelete({ accountNo: req.params.accountNo });
        res.json({ message: 'Customer deleted successfully.' });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.get('/api/admin/transactions', async (req, res) => {
    try {
        const txs = await Transaction.find().sort({ date: -1 });
        res.json(txs);
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/admin/broadcast', async (req, res) => {
    try {
        const { text } = req.body;
        await Broadcast.create({ text, active: true });
        res.json({ message: 'Broadcast published successfully.' });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.get('/api/admin/chats', async (req, res) => {
    try {
        const chats = await Chat.find().sort({ date: 1 });
        const chatMap = {};
        chats.forEach(c => {
            if (!chatMap[c.userPhone]) chatMap[c.userPhone] = [];
            chatMap[c.userPhone].push(c);
        });
        res.json(chatMap);
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/admin/request-action', async (req, res) => {
    try {
        const { adminPhone, adminName, actionType, targetAccountNo, targetName } = req.body;
        await AdminRequest.create({ adminPhone, adminName, actionType, targetAccountNo, targetName });
        res.json({ message: 'Request sent to Super Admin.' });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.get('/api/admin/requests', async (req, res) => {
    try {
        const requests = await AdminRequest.find({ status: 'PENDING' });
        res.json(requests);
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/admin/requests/:id/resolve', async (req, res) => {
    try {
        const { decision } = req.body;
        const reqDoc = await AdminRequest.findById(req.params.id);
        if (!reqDoc) return res.status(404).json({ message: 'Request not found.' });

        reqDoc.status = decision;
        await reqDoc.save();

        if (decision === 'APPROVED' && reqDoc.actionType === 'DELETE_CUSTOMER') {
            await User.findOneAndDelete({ accountNo: reqDoc.targetAccountNo });
        }
        res.json({ message: `Request ${decision.toLowerCase()} successfully.` });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

// ==========================================
// CUSTOMER API ROUTES
// ==========================================
app.post('/api/user/register', async (req, res) => {
    try {
        const { name, phone, email, pin, profilePic } = req.body;
        const existing = await User.findOne({ phone });
        if (existing) return res.status(400).json({ message: 'Phone number already registered.' });

        const accountNo = '10' + Math.floor(10000000 + Math.random() * 90000000);
        await User.create({
            name, phone, email, pin, accountNo,
            accountType: 'Savings',
            balance: 5000.0,
            kycTier: 'Tier 1',
            status: 'PENDING',
            profilePic: profilePic || ''
        });
        res.status(201).json({ message: 'Account created successfully! Pending admin approval.', accountNo });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/user/login', async (req, res) => {
    try {
        const { phone, pin } = req.body;
        const user = await User.findOne({ phone, pin });
        if (!user) return res.status(401).json({ message: 'Invalid credentials.' });
        if (user.status === 'PENDING') return res.status(403).json({ message: 'Account is pending approval.' });
        if (user.status === 'FROZEN') return res.status(403).json({ message: 'Account is frozen.' });

        user.lastLogin = new Date().toLocaleString();
        await user.save();
        res.json(user);
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.get('/api/announcements/latest', async (req, res) => {
    try {
        const broadcasts = await Broadcast.find({ active: true }).sort({ date: -1 });
        res.json(broadcasts);
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.get('/api/user/verify/:accountNo', async (req, res) => {
    try {
        const { accountNo } = req.params;
        const recipient = await User.findOne({ accountNo, status: 'ACTIVE' });
        if (!recipient) return res.json({ found: false });
        res.json({ found: true, fullName: recipient.name, profilePic: recipient.profilePic || '' });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/user/transfer', async (req, res) => {
    try {
        const { senderPhone, recipientAccount, recipientBank, amount, note, pin } = req.body;
        if (amount <= 0) return res.status(400).json({ message: 'Invalid amount.' });

        const sender = await User.findOne({ phone: senderPhone });
        if (!sender) return res.status(404).json({ message: 'Sender not found.' });
        if (sender.pin !== pin) return res.status(401).json({ message: 'Incorrect PIN.' });
        if (sender.balance < amount) return res.status(400).json({ message: 'Insufficient balance.' });

        let recipientName = "External Bank Beneficiary";
        const bank = recipientBank || 'PayDesktop Bank';

        if (bank === 'PayDesktop Bank') {
            const recipient = await User.findOne({ accountNo: recipientAccount });
            if (!recipient) return res.status(404).json({ message: 'Recipient account not found.' });
            if (sender.accountNo === recipient.accountNo) return res.status(400).json({ message: 'Cannot transfer to yourself.' });

            recipient.balance += Number(amount);
            await recipient.save();
            recipientName = recipient.name;
        }

        sender.balance -= Number(amount);
        await sender.save();

        const tx_id = 'TXN' + Math.floor(100000 + Math.random() * 900000);
        await Transaction.create({
            tx_id, senderPhone: sender.phone, senderName: sender.name, senderAccount: sender.accountNo,
            recipientAccount, recipientName, recipientBank: bank,
            amount: Number(amount), type: 'TRANSFER', note: note || 'Funds transfer'
        });

        res.json({ message: `Successfully transferred ₦${Number(amount).toLocaleString()} to ${recipientName} (${bank})`, newBalance: sender.balance, tx_id });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/user/airtime', async (req, res) => {
    try {
        const { phone, amount, network, bumberOrPhone, pin } = req.body;
        const user = await User.findOne({ phone });
        if (!user) return res.status(404).json({ message: 'User not found.' });
        if (user.pin !== pin) return res.status(401).json({ message: 'Incorrect PIN.' });
        if (user.balance < amount) return res.status(400).json({ message: 'Insufficient balance.' });

        user.balance -= Number(amount);
        await user.save();

        const tx_id = 'AIR' + Math.floor(100000 + Math.random() * 900000);
        await Transaction.create({
            tx_id, senderPhone: user.phone, senderName: user.name, senderAccount: user.accountNo,
            amount: Number(amount), type: 'AIRTIME', note: `${network} Airtime recharge for ${bumberOrPhone}`
        });

        res.json({ message: `Successfully purchased ₦${amount} ${network} airtime!`, newBalance: user.balance });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/user/betting', async (req, res) => {
    try {
        const { phone, amount, provider, customerId, pin } = req.body;
        const user = await User.findOne({ phone });
        if (!user) return res.status(404).json({ message: 'User not found.' });
        if (user.pin !== pin) return res.status(401).json({ message: 'Incorrect PIN.' });
        if (user.balance < amount) return res.status(400).json({ message: 'Insufficient balance.' });

        user.balance -= Number(amount);
        await user.save();

        const tx_id = 'BET' + Math.floor(100000 + Math.random() * 900000);
        await Transaction.create({
            tx_id, senderPhone: user.phone, senderName: user.name, senderAccount: user.accountNo,
            amount: Number(amount), type: 'BETTING', note: `${provider} funding for ID: ${customerId}`
        });

        res.json({ message: `Successfully funded ${provider} account with ₦${amount}!`, newBalance: user.balance });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/user/request-card', async (req, res) => {
    try {
        const { phone } = req.body;
        const user = await User.findOne({ phone });
        if (!user) return res.status(404).json({ message: 'User not found.' });

        user.cardStatus = 'PENDING';
        await user.save();
        res.json({ message: 'ATM Card request submitted successfully to Admin.' });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.get('/api/user/beneficiaries/:phone', async (req, res) => {
    try {
        const list = await Beneficiary.find({ userPhone: req.params.phone });
        res.json(list);
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/user/beneficiaries', async (req, res) => {
    try {
        const { phone, name, accountNumber, bankName } = req.body;
        const existing = await Beneficiary.findOne({ userPhone: phone, accountNumber });
        if (!existing) {
            await Beneficiary.create({ userPhone: phone, name, accountNumber, bankName: bankName || 'PayDesktop Bank' });
        }
        res.json({ message: 'Beneficiary saved.' });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.get('/api/user/transactions/:phone', async (req, res) => {
    try {
        const { phone } = req.params;
        const txs = await Transaction.find({ $or: [{ senderPhone: phone }, { recipientPhone: phone }] }).sort({ date: -1 });
        res.json(txs);
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/user/profile/update', async (req, res) => {
    try {
        const { currentPhone, newPhone, newEmail, newPin, profilePic } = req.body;
        const user = await User.findOne({ phone: currentPhone });
        if (!user) return res.status(404).json({ message: 'User not found.' });

        if (newPhone) user.phone = newPhone;
        if (newEmail) user.email = newEmail;
        if (newPin) user.pin = newPin;
        if (profilePic !== undefined) user.profilePic = profilePic;

        await user.save();
        res.json({ message: 'Profile updated successfully', user });
    } catch (err) { res.status(500).json({ message: err.message }); }
});

// ==========================================
// SHAREABLE WEB TRANSFER LINK ROUTES
// ==========================================
app.post('/api/create-transfer-link', async (req, res) => {
    try {
        const { recipientName, bankName, accountNumber, amount } = req.body;
        const token = crypto.randomBytes(16).toString('hex');
        
        await TransferLink.create({
            token,
            recipientName,
            bankName,
            accountNumber,
            amount: Number(amount)
        });

        const shareableLink = `${req.protocol}://${req.get('host')}/pay/${token}`;
        res.json({ success: true, link: shareableLink });
    } catch (err) {
        res.status(500).json({ success: false, message: err.message });
    }
});

app.get('/pay/:token', async (req, res) => {
    try {
        const { token } = req.params;
        const transfer = await TransferLink.findOne({ token });
        if (!transfer) {
            return res.status(404).send('This transfer link is invalid or has expired.');
        }
        res.render('requests', { transfer });
    } catch (err) {
        res.status(500).send('Server Error');
    }
});

// ==========================================
// CHAT API ROUTES
// ==========================================
app.get('/api/chat/:phone', async (req, res) => {
    try {
        const { phone } = req.params;
        const messages = await Chat.find({ userPhone: phone }).sort({ date: 1 });
        res.json(messages);
    } catch (err) { res.status(500).json({ message: err.message }); }
});

app.post('/api/chat/send', async (req, res) => {
    try {
        const { userPhone, senderRole, message } = req.body;
        const chat = await Chat.create({ userPhone, senderRole, message });
        res.json(chat);
    } catch (err) { res.status(500).json({ message: err.message }); }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`PayDesktop Bank server running on port ${PORT}`);
});
