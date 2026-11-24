import { SCREENS } from "@/lib/screens";

export default function ScreensPage() {
  return (
    <main className="page">
      <h1>Design screens</h1>
      <p className="lede">Every screen from the 20 November 2026 CareGrove design package. The live product uses this logo, these photographs, and this layout.</p>
      <div className="screen-grid">
        {SCREENS.map((screen) => (
          <figure key={screen.file} className="card">
            <img src={`/design/${screen.file}`} alt={`${screen.title}, ${screen.surface}`} />
            <figcaption>
              <strong>{screen.title}</strong>
              <div className="meta">{screen.surface}</div>
            </figcaption>
          </figure>
        ))}
      </div>
    </main>
  );
}
