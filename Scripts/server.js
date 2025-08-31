const express = require('express');
const admin = require('firebase-admin');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = 3000;

const serviceAccount = require('../Scripts/tabengine-37a4f-firebase-adminsdk-fbsvc-7be24f48b5.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const auth = admin.auth();

app.use(bodyParser.json());
app.use(express.static('public'));

app.post('/register', async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ error: 'Email e senha são obrigatórios.' });
  }

  try {
    const userRecord = await auth.createUser({
      email,
      password,
    });

    return res.json({ message: 'Usuário criado com sucesso!', uid: userRecord.uid });
  } catch (error) {
    return res.status(400).json({ error: error.message });
  }
});

app.post('/login', async (req, res) => {

  res.json({ message: 'Login gerenciado no front-end via Firebase Auth' });
});

app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
