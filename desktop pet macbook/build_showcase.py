import json
import os

d = r"C:\Users\abhip\.gemini\antigravity\brain\2dbdee45-de09-4c46-b2d5-01d3f0ea321d"
scratch_dir = os.path.join(d, "scratch")
os.makedirs(scratch_dir, exist_ok=True)
b64s = json.load(open(os.path.join(d, "b64s.json")))

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Baby Griffin Archetype Showcase</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    @keyframes gentleFloat {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-7px); }
    }
    @keyframes shadowPulse {
      0%, 100% { transform: scaleX(1); opacity: 0.7; }
      50% { transform: scaleX(0.8); opacity: 0.4; }
    }
    .float-anim {
      animation: gentleFloat 2.6s ease-in-out infinite;
    }
    .shadow-anim {
      animation: shadowPulse 2.6s ease-in-out infinite;
    }
    .pixelated {
      image-rendering: pixelated;
      image-rendering: crisp-edges;
    }
  </style>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-0 m-0 font-sans">
  <div class="py-2 px-1 max-w-3xl mx-auto space-y-3">
    
    <!-- Top Selector Tabs -->
    <div class="flex items-center gap-1.5 overflow-x-auto pb-1 border-b border-[var(--card-border)]">
      <button id="tab-1" onclick="selectVariant('1')" class="tab-btn flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all bg-[var(--primary)] text-[var(--primary-foreground)] border-[var(--primary)] shadow-sm">
        <span class="w-2 h-2 rounded-full bg-amber-400"></span>
        <span>1. Royal Sun</span>
      </button>
      <button id="tab-2" onclick="selectVariant('2')" class="tab-btn flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all bg-[var(--card)] text-[var(--foreground)] border-[var(--border)] hover:bg-[var(--sidebar)]">
        <span class="w-2 h-2 rounded-full bg-pink-400"></span>
        <span>2. Chibi Pip</span>
      </button>
      <button id="tab-3" onclick="selectVariant('3')" class="tab-btn flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all bg-[var(--card)] text-[var(--foreground)] border-[var(--border)] hover:bg-[var(--sidebar)]">
        <span class="w-2 h-2 rounded-full bg-purple-500"></span>
        <span>3. Midnight</span>
      </button>
      <button id="tab-4" onclick="selectVariant('4')" class="tab-btn flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all bg-[var(--card)] text-[var(--foreground)] border-[var(--border)] hover:bg-[var(--sidebar)]">
        <span class="w-2 h-2 rounded-full bg-cyan-400"></span>
        <span>4. Arctic</span>
      </button>
      <button id="tab-5" onclick="selectVariant('5')" class="tab-btn flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all bg-[var(--card)] text-[var(--foreground)] border-[var(--border)] hover:bg-[var(--sidebar)]">
        <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
        <span>5. Sylvan</span>
      </button>
    </div>

    <!-- Main Showcase Card -->
    <div class="grid grid-cols-1 md:grid-cols-12 gap-3 items-center bg-[var(--card)] border border-[var(--card-border)] rounded-xl p-3 shadow-sm">
      
      <!-- Left: Animated Pixel Art Preview -->
      <div class="md:col-span-5 flex flex-col items-center justify-center p-3 rounded-lg bg-[var(--sidebar)] border border-[var(--card-border)] relative min-h-[220px]">
        <span id="archetype-badge" class="absolute top-2 left-2 text-[10px] uppercase font-mono tracking-wider px-2 py-0.5 rounded bg-[var(--background)] text-[var(--muted-foreground)] border border-[var(--border)]">
          Noble Heraldic
        </span>
        <span class="absolute top-2 right-2 text-[10px] font-mono text-[var(--muted-foreground)]">128×128 Preview</span>

        <div class="relative flex flex-col items-center justify-center my-auto">
          <img id="variant-img" src="" alt="Griffin Variant" class="w-32 h-32 pixelated float-anim select-none" />
          <div class="w-20 h-2 bg-black/25 dark:bg-black/50 rounded-full blur-[1px] mt-1 shadow-anim"></div>
        </div>

        <div class="flex items-center gap-1.5 mt-2" id="palette-chips">
          <!-- dynamic swatches -->
        </div>
      </div>

      <!-- Right: Archetype Details & Anatomy Specs -->
      <div class="md:col-span-7 flex flex-col justify-between space-y-2">
        <div>
          <div class="flex items-baseline justify-between">
            <h2 id="variant-title" class="text-base font-bold text-[var(--foreground)]">Royal Sun Griffin</h2>
            <span id="variant-subtitle" class="text-xs text-[var(--muted-foreground)] italic">The Noble Golden Herald</span>
          </div>
          <p id="variant-desc" class="text-xs text-[var(--foreground)] mt-1 leading-relaxed opacity-90">
            Classic mythological griffin: Tawny lion coat, snow-ivory eagle plumage, 3-plume royal crest, curved golden beak, and flame tail tuft.
          </p>
        </div>

        <!-- Visual Anatomy Specs Table -->
        <div class="grid grid-cols-2 gap-1.5 text-xs bg-[var(--background)] p-2 rounded-lg border border-[var(--card-border)]">
          <div>
            <span class="text-[var(--muted-foreground)] font-medium text-[11px] block">Head & Crest:</span>
            <span id="spec-head" class="font-medium text-[var(--foreground)]">Royal 3-Plume Crown</span>
          </div>
          <div>
            <span class="text-[var(--muted-foreground)] font-medium text-[11px] block">Eagle Beak:</span>
            <span id="spec-beak" class="font-medium text-[var(--foreground)]">Sharp Golden Raptor Hook</span>
          </div>
          <div>
            <span class="text-[var(--muted-foreground)] font-medium text-[11px] block">Limbs & Claws:</span>
            <span id="spec-limbs" class="font-medium text-[var(--foreground)]">Separated Paws + Golden Talons</span>
          </div>
          <div>
            <span class="text-[var(--muted-foreground)] font-medium text-[11px] block">Tail & Tuft:</span>
            <span id="spec-tail" class="font-medium text-[var(--foreground)]">S-Curve Flame Tuft</span>
          </div>
        </div>

        <!-- Selection Banner & Action -->
        <div class="pt-1 border-t border-[var(--card-border)] flex items-center justify-between gap-2">
          <span id="selection-hint" class="text-xs text-[var(--muted-foreground)]">
            To apply, tell me: <code class="font-mono px-1 py-0.5 rounded bg-[var(--background)] text-[var(--primary)] font-bold text-[11px]">Use Variant 1</code>
          </span>
          <button id="copy-btn" onclick="applyChoice()" class="text-xs font-semibold px-3 py-1.5 rounded-lg bg-[var(--primary)] text-[var(--primary-foreground)] hover:opacity-90 transition-opacity shrink-0 cursor-pointer">
            Choose Option 1
          </button>
        </div>
      </div>
    </div>

  </div>

  <script>
    const VARIANTS_DATA = {
      '1': {
        name: 'Royal Sun Griffin',
        subtitle: 'The Noble Golden Herald',
        badge: 'Classic Mythic',
        desc: 'The iconic regal heraldry griffin. Warm golden-tawny lion body, snow-ivory eagle ruff, 3-plume crown crest, prominent sharp golden raptor beak, and an elegant S-curved flame tail.',
        img: 'data:image/png;base64,' + 'IMG_1_PLACEHOLDER',
        colors: ['#EB942D', '#FCF8EE', '#FFBE16', '#201008', '#AA4B10'],
        head: '3-Plume Royal Crown',
        beak: 'Curved Golden Raptor Hook',
        limbs: 'Separated Paws + Scaly Talons',
        tail: 'High S-Curve Flame Tuft'
      },
      '2': {
        name: 'Chibi Cloud Griffin',
        subtitle: 'The Ultra-Cute Marshmallow Pip',
        badge: 'Chibi & Cute',
        desc: 'Maximum cuteness baby puffball. Butterscotch honey coat, fluffy whipped-cream downy chest, adorable pastel-pink pom-pom tail, sparkling bright sapphire anime eyes, and a cute button beak.',
        img: 'data:image/png;base64,' + 'IMG_2_PLACEHOLDER',
        colors: ['#F8C473', '#FFF8EE', '#FFD741', '#3C8CE6', '#FFAFBE'],
        head: 'Soft Baby Down Ear Tufts',
        beak: 'Adorable Petite Button Hook',
        limbs: 'Chubby Kitten Paws + Soft Talons',
        tail: 'Fluffy Pink Pom-Pom Puff'
      },
      '3': {
        name: 'Midnight Shadow Griffin',
        subtitle: 'The Arcane Night Stalker',
        badge: 'Arcane Fantasy',
        desc: 'Sleek nocturnal predator. Obsidian panther coat, deep twilight eagle feathers, glowing luminous amethyst eyes, moon-silver raptor beak and claws, with arcane violet wing tips and crescent tail.',
        img: 'data:image/png;base64,' + 'IMG_3_PLACEHOLDER',
        colors: ['#2A2D3E', '#444A62', '#CDDCF0', '#B941F5', '#7D4BC0'],
        head: 'Swept-Back Shadow Horns',
        beak: 'Moon-Silver & Steel Hook',
        limbs: 'Black Panther Paws + Steel Talons',
        tail: 'Glowing Violet Crescent Blade'
      },
      '4': {
        name: 'Arctic Blizzard Griffin',
        subtitle: 'Snow Leopard + Snowy Owl',
        badge: 'Winter Frost',
        desc: 'Majestic frost mountain gryphlet. Snowy owl rounded dome, frosted slate beak, crystalline ice-blue eyes, genuine snow-leopard rosettes on flank, and a thick ringed snow-leopard tail.',
        img: 'data:image/png;base64,' + 'IMG_4_PLACEHOLDER',
        colors: ['#EEF4FA', '#C3D0E0', '#505F73', '#37AFFF', '#A5DAF2'],
        head: 'Snowy Owl Dome + Ear Tufts',
        beak: 'Frosted Glacial Slate Hook',
        limbs: 'Thick Snow-Padded Paws + Frost Talons',
        tail: 'Thick Ringed Leopard Tail'
      },
      '5': {
        name: 'Sylvan Forest Gryphlet',
        subtitle: 'Barn Owl + Woodland Lynx',
        badge: 'Nature Guardian',
        desc: 'Whimsical forest dweller. Heart-shaped ivory barn owl facial disc mask, tall pointed lynx ears with dark whisker tips, soulful hazel-amber eyes, forest sage-green feather tips, and acorn tail tuft.',
        img: 'data:image/png;base64,' + 'IMG_5_PLACEHOLDER',
        colors: ['#D28A44', '#FCF6E8', '#F2E4BC', '#7DA569', '#A5781E'],
        head: 'Heart Face Mask + Lynx Ears',
        beak: 'Slender Ivory-Horn Hook',
        limbs: 'Lynx Rear Paws + Bark Talons',
        tail: 'Acorn / Autumn Leaf Tuft'
      }
    };

    let activeVariant = '1';

    function selectVariant(id) {
      activeVariant = id;
      const data = VARIANTS_DATA[id];

      // Update tabs style
      document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('bg-[var(--primary)]', 'text-[var(--primary-foreground)]', 'border-[var(--primary)]', 'shadow-sm');
        btn.classList.add('bg-[var(--card)]', 'text-[var(--foreground)]', 'border-[var(--border)]');
      });
      const activeTab = document.getElementById('tab-' + id);
      activeTab.classList.remove('bg-[var(--card)]', 'text-[var(--foreground)]', 'border-[var(--border)]');
      activeTab.classList.add('bg-[var(--primary)]', 'text-[var(--primary-foreground)]', 'border-[var(--primary)]', 'shadow-sm');

      // Update Card content
      document.getElementById('archetype-badge').innerText = data.badge;
      document.getElementById('variant-img').src = data.img;
      document.getElementById('variant-title').innerText = data.name;
      document.getElementById('variant-subtitle').innerText = data.subtitle;
      document.getElementById('variant-desc').innerText = data.desc;
      document.getElementById('spec-head').innerText = data.head;
      document.getElementById('spec-beak').innerText = data.beak;
      document.getElementById('spec-limbs').innerText = data.limbs;
      document.getElementById('spec-tail').innerText = data.tail;

      // Palette chips
      const chipsContainer = document.getElementById('palette-chips');
      chipsContainer.innerHTML = '';
      data.colors.forEach(hex => {
        const chip = document.createElement('span');
        chip.className = 'w-4 h-4 rounded-full border border-black/20 dark:border-white/20 shadow-xs inline-block';
        chip.style.backgroundColor = hex;
        chip.title = hex;
        chipsContainer.appendChild(chip);
      });

      // Update CTA
      document.getElementById('selection-hint').innerHTML = 'To apply, tell me: <code class="font-mono px-1 py-0.5 rounded bg-[var(--background)] text-[var(--primary)] font-bold text-[11px]">Use Variant ' + id + ' (' + data.name + ')</code>';
      document.getElementById('copy-btn').innerText = 'Choose Option ' + id;
    }

    function applyChoice() {
      const data = VARIANTS_DATA[activeVariant];
      const hint = document.getElementById('selection-hint');
      hint.innerHTML = '<span class="text-[var(--success)] font-semibold">Selected! Tell me: "Apply Option ' + activeVariant + '"</span>';
    }

    // Init
    selectVariant('1');
  </script>
</body>
</html>
"""

html_template = html_template.replace("IMG_1_PLACEHOLDER", b64s["griffin_variant_1_royal_sun.png"])
html_template = html_template.replace("IMG_2_PLACEHOLDER", b64s["griffin_variant_2_chibi_cloud.png"])
html_template = html_template.replace("IMG_3_PLACEHOLDER", b64s["griffin_variant_3_midnight_shadow.png"])
html_template = html_template.replace("IMG_4_PLACEHOLDER", b64s["griffin_variant_4_arctic_blizzard.png"])
html_template = html_template.replace("IMG_5_PLACEHOLDER", b64s["griffin_variant_5_sylvan_forest.png"])

out_path = os.path.join(scratch_dir, "showcase.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html_template)
print("Generated scratch showcase.html, size:", len(html_template))
