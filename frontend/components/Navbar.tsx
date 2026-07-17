import Link from "next/link";

export default function Navbar() {
  return (
    <header className="border-b border-border">
      <nav className="mx-auto flex max-w-5xl items-center gap-6 px-6 py-4">
        <Link href="/" className="font-semibold">
          AEO Product Ops
        </Link>
        <Link href="/" className="text-sm text-muted hover:text-foreground">
          Home
        </Link>
        <Link href="/history" className="text-sm text-muted hover:text-foreground">
          History
        </Link>
      </nav>
    </header>
  );
}
