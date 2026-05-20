"use client";

import { SignInButton, UserButton, useAuth } from "@clerk/nextjs";

export default function AuthUserMenu() {
  const { isLoaded, isSignedIn } = useAuth();

  if (!isLoaded) {
    return (
      <div
        aria-label="Loading user menu"
        className="h-9 w-9 rounded-full bg-surface-container-high animate-pulse"
      />
    );
  }

  if (isSignedIn) {
    return (
      <div className="h-9 w-9 rounded-full flex items-center justify-center bg-surface-container-high border border-outline-variant/30">
        <UserButton
          appearance={{
            elements: {
              avatarBox: "h-8 w-8",
              userButtonPopoverCard: "bg-surface-container-lowest border border-outline-variant/30",
            },
          }}
        />
      </div>
    );
  }

  return (
    <SignInButton mode="modal" fallbackRedirectUrl="/home">
      <button
        type="button"
        aria-label="Sign in"
        className="h-9 w-9 rounded-full flex items-center justify-center text-on-surface-variant hover:text-primary hover:bg-surface-container-high transition-colors"
      >
        <span className="material-symbols-outlined text-[22px]">login</span>
      </button>
    </SignInButton>
  );
}
