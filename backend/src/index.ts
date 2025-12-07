import express from 'express';
import cors from 'cors';
import session from 'express-session';
import passport from 'passport';
import { Strategy as GitHubStrategy } from 'passport-github2';
import { Strategy as GoogleStrategy } from 'passport-google-oauth20';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:8000',
  credentials: true
}));
app.use(express.json());
app.use(session({
  secret: process.env.SESSION_SECRET || 'your-secret-key',
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    maxAge: 24 * 60 * 60 * 1000 // 24 hours
  }
}));
app.use(passport.initialize());
app.use(passport.session());

// Passport serialization
passport.serializeUser((user: any, done) => {
  done(null, user);
});

passport.deserializeUser((user: any, done) => {
  done(null, user);
});

// GitHub OAuth Strategy
if (process.env.GITHUB_ID && process.env.GITHUB_SECRET) {
  passport.use(new GitHubStrategy({
    clientID: process.env.GITHUB_ID,
    clientSecret: process.env.GITHUB_SECRET,
    callbackURL: `${process.env.BACKEND_URL || 'http://localhost:3001'}/auth/github/callback`
  }, (accessToken: string, refreshToken: string, profile: any, done: any) => {
    return done(null, {
      id: profile.id,
      name: profile.displayName,
      email: profile.emails?.[0]?.value,
      image: profile.photos?.[0]?.value,
      provider: 'github'
    });
  }));
}

// Google OAuth Strategy
if (process.env.GOOGLE_ID && process.env.GOOGLE_SECRET) {
  passport.use(new GoogleStrategy({
    clientID: process.env.GOOGLE_ID,
    clientSecret: process.env.GOOGLE_SECRET,
    callbackURL: `${process.env.BACKEND_URL || 'http://localhost:3001'}/auth/google/callback`
  }, (accessToken: string, refreshToken: string, profile: any, done: any) => {
    return done(null, {
      id: profile.id,
      name: profile.displayName,
      email: profile.emails?.[0]?.value,
      image: profile.photos?.[0]?.value,
      provider: 'google'
    });
  }));
}

// Auth routes
app.get('/auth/github', passport.authenticate('github', { scope: ['user:email'] }));

app.get('/auth/github/callback',
  passport.authenticate('github', { failureRedirect: '/login' }),
  (req, res) => {
    res.redirect(process.env.FRONTEND_URL || 'http://localhost:8000');
  }
);

app.get('/auth/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

app.get('/auth/google/callback',
  passport.authenticate('google', { failureRedirect: '/login' }),
  (req, res) => {
    res.redirect(process.env.FRONTEND_URL || 'http://localhost:8000');
  }
);

app.get('/auth/logout', (req, res) => {
  req.logout(() => {
    res.redirect(process.env.FRONTEND_URL || 'http://localhost:8000');
  });
});

app.get('/auth/user', (req, res) => {
  if (req.isAuthenticated()) {
    res.json({ user: req.user });
  } else {
    res.json({ user: null });
  }
});

// API routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy', service: 'ai-assistant-backend' });
});

app.get('/api/agents', (req, res) => {
  res.json(['assistant', 'coder']);
});

app.get('/api/agents/:name', (req, res) => {
  const agents: Record<string, any> = {
    assistant: {
      name: 'assistant',
      description: 'Main AI assistant for general tasks',
      model: 'gemini-2.5-flash'
    },
    coder: {
      name: 'coder',
      description: 'Specialized coding assistant',
      model: 'gemini-2.5-pro'
    }
  };
  res.json(agents[req.params.name] || { error: 'Agent not found' });
});

// Start server
app.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
  console.log(`GitHub OAuth: ${process.env.GITHUB_ID ? 'Configured' : 'Not configured'}`);
  console.log(`Google OAuth: ${process.env.GOOGLE_ID ? 'Configured' : 'Not configured'}`);
});
