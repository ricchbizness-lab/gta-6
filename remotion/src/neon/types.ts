// Format "neon explainer" : short vertical explicatif, habillage neon/synthwave.
// Tout le branding passe par Brand ; tout le contenu par Scene[].

export type Brand = {
  name: string; // nom du createur / de la chaine (outro)
  tagline: string; // ex. "Tech & gaming"
  avatar?: string; // chemin dans public/ (optionnel : sinon initiales)
  tags: string[]; // pastilles de l'outro
  chapterLabel: string; // "PARTIE", "ETAPE", "PART"...
  colors: {
    primary: string; // titres, contours, glow
    secondary: string; // degrades, accents
    badge: string; // pastille numero de chapitre
    positive: string; // validations, bouton A
    negative: string; // erreurs, bouton B
    panel: string; // fond des cartes
    text: string;
    grid: string; // grille synthwave
  };
  fonts: { title: "kaushan" | "pacifico" | "bebas"; ui: "montserrat" };
};

export type ChecklistItem = { label: string; state: "done" | "locked" | "cross" };

export type Card =
  | { type: "stat"; icon: string; label: string; sub?: string; value?: string; countTo?: number; prefix?: string; lock?: boolean }
  | { type: "compare"; left: { label: string; value: number }; right: { label: string; value: number }; prefix?: string }
  | { type: "badge"; n: number }
  | { type: "checklist"; title: string; items: ChecklistItem[] }
  | { type: "levels"; items: string[] }
  | { type: "gauge"; left: string; right: string; value: number; verdict?: string }
  | { type: "image"; src: string; caption?: string }
  | { type: "choice"; a: string; b: string }
  | { type: "icon"; glyph: string; color?: string }
  | { type: "creator" };

export type Scene = {
  start: number; // secondes
  end: number;
  chapter?: number; // 0 = pas de pastille
  title?: string;
  card?: Card;
  flash?: boolean; // transition flash a l'entree (debut de chapitre)
};

export type Background = { src: string; from: number; to: number };

export type NeonProps = {
  brand: Brand;
  scenes: Scene[];
  backgrounds: Background[];
  voice: string;
  captions: string;
  music?: string;
  musicVolume?: number;
  sfx: boolean;
  durationInSeconds: number;
};
