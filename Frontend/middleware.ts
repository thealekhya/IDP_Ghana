import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isProtectedRoute = createRouteMatcher([
  "/home(.*)",
  "/chat(.*)",
  "/map(.*)",
  "/anomalies(.*)",
]);

export default clerkMiddleware(async (auth, request) => {
  if (isProtectedRoute(request)) {
    await auth.protect();
  }
}, {
  signInUrl: "/",
  signUpUrl: "/",
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.[0-9a-zA-Z]+$).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};
