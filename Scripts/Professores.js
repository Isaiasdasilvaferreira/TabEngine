const firebaseConfig = {
  apiKey: "AIzaSyDM0lPwywlJsjozXZiEb6hbZtC4RcaqOXM",
  authDomain: "tabengine-37a4f.firebaseapp.com",
  projectId: "tabengine-37a4f",
  storageBucket: "tabengine-37a4f.appspot.com",
  messagingSenderId: "262670013449",
  appId: "1:262670013449:web:fc18d33b6fc16c313814d8",
  measurementId: "G-7K8EW4FD1R"
};

firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

function isProfessor(email) {
  email = email.toLowerCase();
  return email.endsWith('.prof@etec.sp.gov.br');
}

auth.onAuthStateChanged(user => {
  if (!user) {
    window.location.href = 'inicio.html';
    return;
  }

  const email = user.email.toLowerCase();

  if (isProfessor(email)) {
 
    document.body.style.visibility = 'visible';
  } else {
   
    window.location.href = 'index.html';
  }
});
