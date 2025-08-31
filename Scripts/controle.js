const firebaseConfig = {
  apiKey: "AIzaSyDM0lPwywlJsjozXZiEb6hbZtC4RcaqOXM",
  authDomain: "tabengine-37a4f.firebaseapp.com",
  projectId: "tabengine-37a4f",
};

firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

function isGestaoEscolar(email) {
  email = email.toLowerCase();
  if (!email.endsWith('@cps.sp.gov.br')) return false;
  const prefix = email.split('@')[0];
  const regex = /^e[a-z]+(\d{3,})\d*$/;
  return regex.test(prefix);
}

auth.onAuthStateChanged(async (user) => {
  if (user) {
    const email = user.email.toLowerCase();

    if (isGestaoEscolar(email)) {
      document.getElementById('menu-links').style.display = 'block';
      document.getElementById('msg-acesso').textContent = '';
    } else {
      document.getElementById('menu-links').style.display = 'none';
      document.getElementById('msg-acesso').textContent = 'Acesso restrito a contas da gestão escolar.';
    }
  } else {
    document.getElementById('menu-links').style.display = 'none';
    document.getElementById('msg-acesso').textContent = 'Faça login para acessar o menu.';
  }
});
