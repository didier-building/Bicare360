import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import './HomePage.css';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { checkAuth } = useAuthStore();
  const [checkingAuth, setCheckingAuth] = useState(true);

  const careJourneySteps = [
    {
      title: 'Discharge Plan Captured',
      description: 'Clinical instructions and risk signals are organized from day one of home recovery.',
    },
    {
      title: 'Care Team Aligned',
      description: 'Nurses, caregivers, and patients work from the same care context and priorities.',
    },
    {
      title: 'Daily Follow-Up Tracked',
      description: 'Appointments, medications, and home-care tasks stay visible and measurable.',
    },
    {
      title: 'Early Alerts Trigger Action',
      description: 'Missed medication, missed appointments, and risk changes prompt timely intervention.',
    },
  ];

  const audienceCards = [
    {
      title: 'Patients and Families',
      description: 'Follow your care plan with appointments, medications, daily goals (including nutrition), and key medical updates.',
      href: '/patient/login',
      signupHref: '/patient/register',
      cta: 'Patient Login',
      ctaSignup: 'Create Account',
      toneClass: 'home-card-patient',
    },
    {
      title: 'Nurses and Care Teams',
      description: 'Monitor patient follow-up, manage alerts, review care progress, and coordinate next care actions.',
      href: '/login',
      cta: 'Staff Login',
      toneClass: 'home-card-staff',
    },
    {
      title: 'Caregivers',
      description: 'Manage bookings, track home-care visits, and support patients through coordinated communication.',
      href: '/caregiver/login',
      cta: 'Caregiver Login',
      toneClass: 'home-card-caregiver',
    },
  ];

  useEffect(() => {
    let isActive = true;

    const route = async () => {
      await checkAuth();

      if (!isActive) {
        return;
      }

      const { isAuthenticated, user } = useAuthStore.getState();

      if (isAuthenticated) {
        if (user?.role === 'nurse' || user?.role === 'staff') {
          navigate('/dashboard', { replace: true });
        } else if (user?.role === 'caregiver') {
          navigate('/caregiver/dashboard', { replace: true });
        } else {
          navigate('/patient/dashboard', { replace: true });
        }

        return;
      }

      setCheckingAuth(false);
    };

    route();

    return () => {
      isActive = false;
    };
  }, [checkAuth, navigate]);

  if (checkingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f8faf7]">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Preparing your care workspace...</p>
        </div>
      </div>
    );
  }

  return (
    <main className="home-root">
      <header className="home-shell home-brand-bar home-stagger">
        <Link to="/" className="home-brand-link" aria-label="BiCare360 home">
          <img src="/logo.png" alt="BiCare360 logo" className="home-brand-logo" />
          <span className="home-brand-name">BiCare360</span>
        </Link>
        <Link to="/login-selection" className="home-brand-login">Portal Login</Link>
      </header>

      <section className="home-hero">
        <div className="home-hero-atmosphere" aria-hidden="true" />
        <div className="home-shell home-stagger">
          <p className="home-kicker">Post-Discharge Continuity Platform</p>
          <h1 className="home-headline">From Hospital Discharge to Confident Home Recovery</h1>
          <p className="home-subhead">
            BiCare360 connects patients, nurses, and caregivers in one coordinated journey with reminders,
            alerts, and real-time communication.
          </p>
          <div className="home-cta-row">
            <Link to="/patient/register" className="home-btn home-btn-primary">Sign Up as Patient</Link>
            <Link to="/login-selection" className="home-btn home-btn-secondary">Already Have Account?</Link>
          </div>
          <p className="home-caption">Built for Rwanda&apos;s healthcare delivery context.</p>
        </div>
      </section>

      <section className="home-shell home-grid-highlights home-stagger">
        <article className="home-highlight-box">
          <p className="home-highlight-number">3</p>
          <p className="home-highlight-label">Integrated Portals</p>
          <p className="home-highlight-text">Patient, staff, and caregiver experiences designed around one care journey.</p>
        </article>
        <article className="home-highlight-box">
          <p className="home-highlight-number">24/7</p>
          <p className="home-highlight-label">Care Visibility</p>
          <p className="home-highlight-text">Appointments, medication adherence, and alerts in one operational view.</p>
        </article>
        <article className="home-highlight-box">
          <p className="home-highlight-number">1</p>
          <p className="home-highlight-label">Coordinated Journey</p>
          <p className="home-highlight-text">From discharge instructions to home follow-up and recovery outcomes.</p>
        </article>
      </section>

      <section className="home-shell home-section home-stagger">
        <div className="home-section-head">
          <h2>How BiCare360 Works</h2>
          <p>Every step reduces care fragmentation and keeps people aligned.</p>
        </div>
        <div className="home-journey-grid">
          {careJourneySteps.map((step, index) => (
            <article key={step.title} className="home-journey-card">
              <span className="home-step-pill">Step {index + 1}</span>
              <h3>{step.title}</h3>
              <p>{step.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="home-shell home-section home-stagger">
        <div className="home-section-head">
          <h2>Choose Your Experience</h2>
          <p>Each role gets a focused workflow while staying connected to the same patient journey.</p>
        </div>
        <div className="home-audience-grid">
          {audienceCards.map((card) => (
            <article key={card.title} className={`home-audience-card ${card.toneClass}`}>
              <h3>{card.title}</h3>
              <p>{card.description}</p>
              <div className="home-role-actions">
                <Link to={card.href} className="home-role-link">{card.cta}</Link>
                {(card as any).signupHref && (
                  <Link to={(card as any).signupHref} className="home-role-link home-role-link-secondary">{(card as any).ctaSignup}</Link>
                )}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="home-shell home-section">
        <div className="home-rwanda-panel home-stagger">
          <h2>Rwanda-First by Design</h2>
          <p>
            National ID workflows, local communication patterns, and multilingual support direction are built
            into the platform to make coordination practical in everyday care delivery.
          </p>
          <div className="home-tag-row">
            <span>National ID Workflows</span>
            <span>Caregiver Coordination</span>
            <span>Medication Adherence Alerts</span>
            <span>Appointment Follow-Up</span>
          </div>
        </div>
      </section>

      <section className="home-shell home-final-cta home-stagger">
        <h2>Ready to Get Started?</h2>
        <p>New users can sign up, or existing users can log in to access their portal.</p>
        <div className="home-cta-dual-row">
          <div className="home-cta-group">
            <p className="home-cta-group-label">New Patient?</p>
            <Link to="/patient/register" className="home-btn home-btn-primary">Create Patient Account</Link>
          </div>
          <div className="home-cta-group">
            <p className="home-cta-group-label">Have an Account?</p>
            <Link to="/login-selection" className="home-btn home-btn-secondary">Sign In Here</Link>
          </div>
        </div>
      </section>

      <section className="home-shell home-trust-signals home-stagger">
        <div className="home-trust-header">
          <p className="home-trust-label">Why BiCare360 Patients & Teams Choose Us</p>
        </div>
        <div className="home-trust-grid">
          <article className="home-trust-card">
            <div className="home-trust-icon">🔒</div>
            <h3>Role-Based Secure Access</h3>
            <p>Every user gets role-specific, protected access to ensure privacy and appropriate care coordination.</p>
          </article>
          <article className="home-trust-card">
            <div className="home-trust-icon">👥</div>
            <h3>Built for Patients, Caregivers & Care Teams</h3>
            <p>Platform designed for all care stakeholders to work together seamlessly in one coordinated journey.</p>
          </article>
          <article className="home-trust-card">
            <div className="home-trust-icon">✓</div>
            <h3>Private, Coordinated Home-Care Support</h3>
            <p>Supports safer continuity of care from discharge to home with encrypted communication and alerts.</p>
          </article>
        </div>
      </section>
    </main>
  );
};

export default HomePage;
