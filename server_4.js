const express = require('express');
const mongoose = require('mongoose');
const session = require('express-session');
const bcrypt = require('bcryptjs');
const PDFDocument = require('pdfkit');

const User = require('./models/User');
const Transaction = require('./models/Transaction');

const app = express();

// Middleware Configuration
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.set('view engine', 'ejs');

app.use(session({
  secret: 'paydesktopbank_secure_secret_key',
  resave: false,
  saveUninitialized: false
}));

// Database Connection & Default Super Admin Auto-Seeding
mongoose.connect('mongodb://localhost:27017/paydesktopbank', {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
  .then(async () => {
    console.log('MongoDB Connected Successfully');

    // Auto-create default Super Admin if none exists
    try {
      const adminExists = await User.findOne({ role: 'super_admin' });
      if (!adminExists) {
        const hashedPassword = await bcrypt.hash('admin123', 10);
        await User.create({
          username: 'superadmin',
          email: 'admin@paydesktopbank.com',
          password: hashedPassword,
          requestedRole: 'super_admin',
          role: 'super_admin',
          status: 'approved'
        });
        console.log('Default Super Admin initialized: username -> superadmin | password -> admin123');
      }
    } catch (err) {
      console.log('Error seeding default admin:', err);
    }
  })
  .catch(err => console.log('DB Connection Error:', err));


// --- RBAC MIDDLEWARE ---
function isAuthenticated(req, res, next) {
  if (req.session.user && req.session.user.status === 'approved') {
    return next();
  }
  res.redirect('/login');
}

function verifyAdminPortalAccess(req, res, next) {
  if (req.session.user && req.session.user.status === 'approved') {
    if (['super_admin', 'agent_admin'].includes(req.session.user.role)) {
      return next();
    }
  }
  return res.status(403).send('Access Denied: Regular customers cannot access the Admin Portal.');
}

function verifySuperAdmin(req, res, next) {
  if (req.session.user && req.session.user.role === 'super_admin' && req.session.user.status === 'approved') {
    return next();
  }
  return res.status(403).send('Access Denied: Super Admin privileges required.');
}

function verifyAgentRestrictions(req, res, next) {
  if (req.session.user && req.session.user.role === 'agent_admin') {
    // Agent Admins cannot post broadcasts or delete admin accounts
    if (req.path.includes('/broadcast') || req.path.includes('/delete-admin')) {
      return res.status(403).send('Restricted: Agent Admins cannot post channel broadcasts or delete admin accounts.');
    }
  }
  next();
}


// --- AUTHENTICATION & ACCOUNT REQUEST ROUTES ---

app.get('/login', (req, res) => {
  res.render('login', { error: null });
});

app.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    const user = await User.findOne({ username });

    if (!user || !(await bcrypt.compare(password, user.password))) {
      return res.render('login', { error: 'Invalid username or password.' });
    }

    if (user.status === 'pending') {
      return res.render('login', { error: 'Your account request is still pending Super Admin approval.' });
    }

    if (user.status === 'rejected') {
      return res.render('login', { error: 'Your account request has been rejected.' });
    }

    req.session.user = {
      id: user._id,
      username: user.username,
      role: user.role,
      status: user.status
    };

    if (['super_admin', 'agent_admin'].includes(user.role)) {
      return res.redirect('/admin/dashboard');
    } else {
      return res.redirect('/dashboard');
    }
  } catch (err) {
    console.error(err);
    res.status(500).send('Server Error');
  }
});

// Create Account Request (Under Login Page)
app.post('/request-account', async (req, res) => {
  try {
    const { username, email, password, requestedRole } = req.body;

    const existingUser = await User.findOne({ $or: [{ username }, { email }] });
    if (existingUser) {
      return res.render('login', { error: 'Username or Email is already registered.' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const newUser = new User({
      username,
      email,
      password: hashedPassword,
      requestedRole,
      status: 'pending'
    });

    await newUser.save();
    res.render('login', { error: 'Account request submitted successfully! Awaiting Super Admin review.' });
  } catch (err) {
    console.error(err);
    res.status(500).send('Server Error');
  }
});


// --- ADMIN PORTAL ROUTES ---

app.get('/admin/dashboard', isAuthenticated, verifyAdminPortalAccess, verifyAgentRestrictions, async (req, res) => {
  res.send(`<h1>Admin Portal Dashboard</h1><p>Welcome, ${req.session.user.username} (${req.session.user.role})</p><a href="/admin/requests">View Account Requests</a>`);
});

// Super Admin Request Management Panel
app.get('/admin/requests', isAuthenticated, verifySuperAdmin, async (req, res) => {
  try {
    const requests = await User.find({ status: 'pending' });
    res.render('admin/requests', { requests, user: req.session.user });
  } catch (err) {
    console.error(err);
    res.status(500).send('Server Error');
  }
});

// Accept or Reject Request Actions
app.post('/admin/requests/:id/:action', isAuthenticated, verifySuperAdmin, async (req, res) => {
  try {
    const { id, action } = req.params;
    const targetUser = await User.findById(id);

    if (!targetUser) return res.status(404).send('User not found');

    if (action === 'accept') {
      targetUser.status = 'approved';
      targetUser.role = targetUser.requestedRole; // Assign requested type: super_admin, agent_admin, customer
    } else if (action === 'reject') {
      targetUser.status = 'rejected';
    }

    await targetUser.save();
    res.redirect('/admin/requests');
  } catch (err) {
    console.error(err);
    res.status(500).send('Server Error');
  }
});

// Restricted Admin Actions
app.post('/admin/broadcast', isAuthenticated, verifyAdminPortalAccess, verifyAgentRestrictions, (req, res) => {
  res.send('Broadcast message posted successfully to channel.');
});

app.post('/admin/delete-admin/:id', isAuthenticated, verifyAdminPortalAccess, verifyAgentRestrictions, verifySuperAdmin, async (req, res) => {
  await User.findByIdAndDelete(req.params.id);
  res.send('Admin account deleted.');
});


// --- CUSTOMER PORTAL & TRANSACTION ROUTES ---

app.get('/dashboard', isAuthenticated, async (req, res) => {
  if (['super_admin', 'agent_admin'].includes(req.session.user.role)) {
    return res.redirect('/admin/dashboard');
  }

  try {
    // Transaction Filtering & Search Support
    const { startDate, endDate, transferType } = req.query;
    let query = { sender: req.session.user.username };

    if (startDate && endDate) {
      query.date = { $gte: new Date(startDate), $lte: new Date(endDate) };
    }
    if (transferType) {
      query.transferType = transferType;
    }

    const transactions = await Transaction.find(query);
    res.send(`<h1>Customer Dashboard</h1><p>Welcome ${req.session.user.username}</p><h2>Your Transactions</h2><ul>` +
      transactions.map(t => `<li>${t.transferType} - $${t.amount} to ${t.recipient} | <a href="/receipt/${t._id}">Download PDF Receipt</a></li>`).join('') +
      `</ul>`);
  } catch (err) {
    console.error(err);
    res.status(500).send('Server Error');
  }
});

// Automated PDF Receipt Generator
app.get('/receipt/:id', isAuthenticated, async (req, res) => {
  try {
    const tx = await Transaction.findById(req.params.id);
    if (!tx) return res.status(404).send('Transaction not found');

    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename=receipt-${tx._id}.pdf`);

    const doc = new PDFDocument();
    doc.pipe(res);
    doc.fontSize(22).text('PayDesktopBank', { align: 'center' });
    doc.fontSize(14).text('Official Transaction Receipt', { align: 'center' });
    doc.moveDown();
    doc.fontSize(12).text(`Transaction ID: ${tx._id}`);
    doc.text(`Sender: ${tx.sender}`);
    doc.text(`Recipient: ${tx.recipient}`);
    doc.text(`Amount: $${tx.amount}`);
    doc.text(`Transfer Type: ${tx.transferType}`);
    doc.text(`Date: ${tx.date.toUTCString()}`);
    doc.moveDown();
    doc.text('Thank you for banking with PayDesktopBank.', { align: 'center' });
    doc.end();
  } catch (err) {
    console.error(err);
    res.status(500).send('Server Error');
  }
});

// Start Application Server
app.listen(3000, () => {
  console.log('PayDesktopBank server is running on http://localhost:3000');
});