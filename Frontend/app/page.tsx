import { SignIn } from "@clerk/nextjs";
import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";

export default async function LoginPage() {
  const { userId } = await auth();

  if (userId) {
    redirect("/home");
  }

  return (
    <main className="min-h-screen w-full bg-surface text-on-surface flex">
      <section className="hidden lg:flex w-1/2 relative bg-surface-container-highest overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage:
              "url('https://lh3.googleusercontent.com/aida-public/AB6AXuB5wKtyihx-wejlpGhyNt-hNOm8GiNVNmOrouRfTDe5qa-53E5DfnPBGRwZIIWzXlz17V-f26bjHWN7IJ5t2ZhDGdgwPFj7rGLbs8uki3LaWuYFMR37fWdlMK0HtkK0_UydmDiqrniKun61Gasw3w7YB8vzdIqADYHGenmoT2fL8nt2Qf7NPJFn5BFOyGGL1S-i_nDBiSNy88IBzH1rPyiX2SXgFaPtO2oniO9VgQscEU79cTjBC8pW0qvb-Ivbt5E6jEoKsag0K0y7')",
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background/90 via-background/55 to-transparent" />
        <div className="absolute bottom-12 left-12 right-12">
          <h1 className="font-display-lg text-display-lg text-primary tracking-tight mb-3">
            Sankofa AI
          </h1>
          <p className="font-body-lg text-body-lg text-on-surface-variant max-w-xl">
            Bridging Ghana&apos;s medical data gap with secure medical intelligence.
          </p>
        </div>
      </section>

      <section className="w-full lg:w-1/2 min-h-screen flex flex-col justify-center px-4 sm:px-8 py-12">
        <div className="max-w-md w-full mx-auto flex flex-col items-center gap-8">
          <div className="text-center">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              alt="Sankofa Health Logo"
              className="h-16 w-16 mb-4 mx-auto rounded-full object-cover"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuAum3m4zs7-RJwCvcE-JhB52nMps1jxy5l6iws17tBu7dqk-2DBg_g9DMWGtUplT-8rBP24vOEiCssdLx_z5p0vVGVrE7blpPfqn4ZxMS7RlN9ZdZmoNL4myqjDp5a8AysE-PzNu5cgBVJ22l02Hk40awEKg157eHAff7lDCcjfJWwdOZpYID1ENseIzcAsQi-xx78TpgAP8L164Q0o07wrvIaz-TObPX6mDkip4L8bb-18SEMZky5Q6QQnB2YVfnz7dWXKZb2HtAEn"
            />
            <h1 className="font-headline-md text-headline-md text-primary font-bold">
              Welcome to Sankofa AI
            </h1>
            <p className="mt-2 font-body-md text-on-surface-variant">
              Sign in to continue to your healthcare workspace.
            </p>
          </div>

          <SignIn
            routing="hash"
            fallbackRedirectUrl="/home"
            signUpFallbackRedirectUrl="/home"
            appearance={{
              elements: {
                rootBox: "w-full",
                cardBox: "w-full",
                card: "bg-surface-container-lowest border border-outline-variant/30 shadow-xl",
              },
            }}
          />
        </div>
      </section>
    </main>
  );
}
