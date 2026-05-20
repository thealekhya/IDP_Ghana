import Link from "next/link";
import AuthUserMenu from "../AuthUserMenu";

export default function HomePage() {
  return (
    <div className="bg-background text-on-background font-body-md text-body-md antialiased min-h-screen flex flex-col">
      {/* TopNavBar */}
      <header className="bg-surface/80 dark:bg-surface-dim/80 backdrop-blur-md border-b border-outline-variant/30 fixed top-0 left-0 w-full z-50 flex justify-between items-center px-4 md:px-margin-desktop h-16">
        <div className="flex items-center gap-2">
          <span className="font-headline-md text-headline-md font-bold text-primary tracking-tight">
            Sankofa AI
          </span>
        </div>
        <div className="flex items-center gap-4 hidden">
          {/* Search Bar placeholder */}
        </div>
        <div className="flex items-center gap-4">
          <AuthUserMenu />
        </div>
      </header>

      <main className="flex-grow pt-16">
        {/* Hero Section */}
        <section className="relative overflow-hidden bg-surface-container-lowest py-20 lg:py-32 flex flex-col items-center justify-center text-center px-4">
          <div
            className="absolute inset-0 z-0 opacity-10 pointer-events-none"
            style={{
              backgroundImage:
                "radial-gradient(circle at 50% 50%, #8ed5ff 0%, transparent 50%)",
            }}
          ></div>
          <div className="z-10 max-w-4xl mx-auto flex flex-col items-center">
            <div className="w-24 h-24 rounded-xl mb-8 flex items-center justify-center shadow-lg relative overflow-hidden">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                alt="Sankofa Health Logo"
                className="w-full h-full object-cover"
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuAum3m4zs7-RJwCvcE-JhB52nMps1jxy5l6iws17tBu7dqk-2DBg_g9DMWGtUplT-8rBP24vOEiCssdLx_z5p0vVGVrE7blpPfqn4ZxMS7RlN9ZdZmoNL4myqjDp5a8AysE-PzNu5cgBVJ22l02Hk40awEKg157eHAff7lDCcjfJWwdOZpYID1ENseIzcAsQi-xx78TpgAP8L164Q0o07wrvIaz-TObPX6mDkip4L8bb-18SEMZky5Q6QQnB2YVfnz7dWXKZb2HtAEn"
              />
            </div>
            <div className="flex items-center gap-2 mb-4 animate-fade-in">
              <div className="flex h-3 w-8 overflow-hidden rounded-full shadow-sm">
                <div className="h-full w-1/3 bg-[#EF3340]"></div>
                <div className="h-full w-1/3 bg-[#FFD100] flex items-center justify-center">
                  <div className="w-1.5 h-1.5 bg-black rotate-45"></div>
                </div>
                <div className="h-full w-1/3 bg-[#009739]"></div>
              </div>
              <span className="font-label-sm text-label-sm text-secondary tracking-[0.2em] uppercase">
                Empowering Ghana
              </span>
            </div>
            <h1 className="font-display-lg text-display-lg md:text-5xl lg:text-6xl text-primary mb-6 max-w-3xl">
              Bridging Ghana's Medical Deserts
            </h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant mb-10 max-w-2xl">
              Empowering healthcare workers with agentic AI to analyze complex
              medical data, significantly reducing treatment planning time and
              delivering life-saving insights where they are needed most.
            </p>
            <p className="font-headline-md text-headline-md text-primary-fixed italic mb-10 max-w-2xl opacity-90">
              "Empowering every Ghanaian community with the intelligence to heal."
            </p>
            <div className="flex flex-col sm:flex-row gap-4 flex-wrap justify-center">
              <Link href="/chat" className="bg-primary text-on-primary font-label-sm text-label-sm px-8 py-4 rounded-full hover:bg-primary-container hover:text-on-primary-container transition-all shadow-md inline-block">
                Explore Insights
              </Link>
              <Link href="/map" className="bg-secondary-container text-on-secondary-container font-label-sm text-label-sm px-8 py-4 rounded-full hover:bg-secondary transition-all shadow-md inline-block">
                View Healthcare Map
              </Link>
              <Link href="/anomalies" className="bg-tertiary text-on-tertiary font-label-sm text-label-sm px-8 py-4 rounded-full hover:bg-tertiary-container hover:text-on-tertiary-container transition-all shadow-md inline-block">
                Data Integrity Dashboard
              </Link>
            </div>
          </div>

          {/* Bento Grid Stats Indicator */}
          <div className="mt-16 z-10 w-full max-w-5xl px-4 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-surface rounded-xl p-6 border border-outline-variant/30 flex flex-col items-center justify-center">
              <span
                className="material-symbols-outlined text-secondary text-4xl mb-2"
                data-icon="timer"
              >
                timer
              </span>
              <h3 className="font-headline-md text-headline-md text-on-surface">
                100x
              </h3>
              <p className="font-body-md text-body-md text-on-surface-variant text-center">
                Reduction in treatment planning time
              </p>
            </div>
            <div className="bg-surface rounded-xl p-6 border border-outline-variant/30 flex flex-col items-center justify-center">
              <span
                className="material-symbols-outlined text-primary text-4xl mb-2"
                data-icon="health_and_safety"
              >
                health_and_safety
              </span>
              <h3 className="font-headline-md text-headline-md text-on-surface">
                Data-Driven
              </h3>
              <p className="font-body-md text-body-md text-on-surface-variant text-center">
                Intelligent synthesis of medical records
              </p>
            </div>
            <div className="bg-surface rounded-xl p-6 border border-outline-variant/30 flex flex-col items-center justify-center">
              <span
                className="material-symbols-outlined text-tertiary text-4xl mb-2"
                data-icon="location_on"
              >
                location_on
              </span>
              <h3 className="font-headline-md text-headline-md text-on-surface">
                Targeted
              </h3>
              <p className="font-body-md text-body-md text-on-surface-variant text-center">
                Identifying and supporting high-need areas
              </p>
            </div>
          </div>
        </section>

        {/* How it Works Section */}
        <section className="py-20 bg-surface-container-low px-4 md:px-margin-desktop">
          <div className="max-w-max-width mx-auto">
            <div className="text-center mb-16">
              <h2 className="font-headline-md text-headline-md text-primary mb-4 uppercase tracking-widest font-label-sm text-label-sm">
                The Process
              </h2>
              <h3 className="font-display-lg text-display-lg text-on-surface">
                How Sankofa AI Works
              </h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* Step 1: IDP */}
              <div className="bg-surface-container-lowest rounded-xl p-8 border border-outline-variant/20 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                  <span
                    className="material-symbols-outlined text-8xl text-primary"
                    data-icon="document_scanner"
                  >
                    document_scanner
                  </span>
                </div>
                <div className="w-12 h-12 bg-primary-container text-on-primary-container rounded-full flex items-center justify-center mb-6 font-headline-md text-headline-md">
                  1
                </div>
                <h4 className="font-headline-md text-headline-md text-on-surface mb-3">
                  Intelligent Document Processing
                </h4>
                <p className="font-body-md text-body-md text-on-surface-variant">
                  Extracting critical data from unstructured medical documents,
                  handwritten notes, and legacy systems with high accuracy.
                </p>
              </div>

              {/* Step 2: Synthesis */}
              <div className="bg-surface-container-lowest rounded-xl p-8 border border-outline-variant/20 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                  <span
                    className="material-symbols-outlined text-8xl text-secondary"
                    data-icon="insights"
                  >
                    insights
                  </span>
                </div>
                <div className="w-12 h-12 bg-secondary-container text-on-secondary-container rounded-full flex items-center justify-center mb-6 font-headline-md text-headline-md">
                  2
                </div>
                <h4 className="font-headline-md text-headline-md text-on-surface mb-3">
                  Intelligent Synthesis
                </h4>
                <p className="font-body-md text-body-md text-on-surface-variant">
                  Correlating extracted data points to identify patterns, treatment
                  histories, and potential diagnostic gaps across populations.
                </p>
              </div>

              {/* Step 3: Planning */}
              <div className="bg-surface-container-lowest rounded-xl p-8 border border-outline-variant/20 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                  <span
                    className="material-symbols-outlined text-8xl text-tertiary"
                    data-icon="architecture"
                  >
                    architecture
                  </span>
                </div>
                <div className="w-12 h-12 bg-tertiary-container text-on-tertiary-container rounded-full flex items-center justify-center mb-6 font-headline-md text-headline-md">
                  3
                </div>
                <h4 className="font-headline-md text-headline-md text-on-surface mb-3">
                  Agentic Planning System
                </h4>
                <p className="font-body-md text-body-md text-on-surface-variant">
                  Generating actionable treatment plans and resource allocation
                  strategies, reducing administrative burden and accelerating care
                  delivery.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full py-12 px-4 md:px-margin-desktop flex flex-col md:flex-row justify-between items-center gap-8 bg-surface-container-highest dark:bg-surface-dim border-t border-outline-variant/30">
        <div className="flex items-center gap-2">
          <span className="font-headline-md text-headline-md font-bold text-on-surface">
            Sankofa AI
          </span>
        </div>
        <p className="font-body-md text-body-md text-on-surface-variant">
          © 2024 Sankofa AI. Bridging Ghana's medical data gap.
        </p>
        <nav className="flex gap-6">
          <Link
            className="font-label-sm text-label-sm text-on-surface-variant dark:text-surface-variant hover:text-primary transition-all hover:opacity-90 underline"
            href="#"
          >
            Mission
          </Link>
          <Link
            className="font-label-sm text-label-sm text-on-surface-variant dark:text-surface-variant hover:text-primary transition-all hover:opacity-90 underline"
            href="#"
          >
            Privacy
          </Link>
          <Link
            className="font-label-sm text-label-sm text-on-surface-variant dark:text-surface-variant hover:text-primary transition-all hover:opacity-90 underline"
            href="#"
          >
            Terms
          </Link>
          <Link
            className="font-label-sm text-label-sm text-on-surface-variant dark:text-surface-variant hover:text-primary transition-all hover:opacity-90 underline"
            href="#"
          >
            API Docs
          </Link>
        </nav>
      </footer>
    </div>
  );
}
