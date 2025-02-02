export default function ProductPreview() {
  return (
    <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-20">
      <div className="relative rounded-lg overflow-hidden border border-border shadow-2xl">
        <div className="absolute inset-0 bg-gradient-to-tr from-primary/10 via-accent/10 to-transparent" />
        <img
          src="/hero.jpeg"
          alt="GitScribe AI Documentation Interface"
          className="w-full h-auto"
        />
      </div>

      {/* Ambient glow effect */}
      <div className="absolute -inset-x-20 top-0 h-[500px] bg-gradient-conic from-primary via-accent to-primary opacity-30 blur-3xl" />
    </div>
  );
}
