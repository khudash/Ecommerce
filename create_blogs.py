import os
import shutil
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from store.models import BlogPost

os.makedirs('media/blog', exist_ok=True)

# Copy 3 images
img1_src = 'media/products/hair_oil.png'
img2_src = 'media/hero/hair_oil_2.png'
img3_src = 'media/products/hair_oil_3.png'

if os.path.exists(img1_src):
    shutil.copy(img1_src, 'media/blog/blog_1.png')
if os.path.exists(img2_src):
    shutil.copy(img2_src, 'media/blog/blog_2.png')
if os.path.exists(img3_src):
    shutil.copy(img3_src, 'media/blog/blog_3.png')

posts_data = [
    {
        'title': '5 Powerhouse Natural Ingredients That Supercharge Hair Growth',
        'slug': '5-powerhouse-natural-ingredients-that-supercharge-hair-growth',
        'category': 'ingredients',
        'author': 'HairGlow Wellness Team',
        'read_time': 5,
        'image': 'blog/blog_1.png',
        'is_published': True,
        'is_featured': True,
        'excerpt': 'Discover the science-backed herbal extracts like Rosemary, Bhringraj, and Castor Oil that revitalize dormant follicles and stimulate natural thickness.',
        'content': """<p class="lead">Healthy, luscious hair starts from the root. While chemical-heavy treatments promise overnight wonders, true long-lasting hair vitality comes from potent, cold-pressed botanical extracts that nourish the scalp at a cellular level.</p>

<h2>1. Cold-Pressed Rosemary Extract</h2>
<p>Rosemary has been clinically proven to improve microcirculation around hair roots. Its active compound, carnosic acid, rejuvenates nerve endings and supports follicle regeneration without unwanted scalp irritation or redness.</p>

<h2>2. Ayurvedic Bhringraj (The King of Hair)</h2>
<p>In traditional holistic medicine, Bhringraj is revered as the ultimate elixir for premature thinning and shedding. Packed with essential minerals and bioflavonoids, it deeply penetrates the scalp barrier to strengthen weak strands from the root.</p>

<h2>3. Pure Virgin Castor & Moroccan Argan Oil</h2>
<p>Ricinoleic acid in pure castor oil delivers deep hydration while sealing split ends and locking in moisture. Paired with Moroccan Argan oil rich in Vitamin E, it shields your hair shafts against everyday pollution, sun exposure, and heat damage.</p>

<blockquote>
"Consistent application of nutrient-dense botanical oils stimulates microcirculation by up to 40%, allowing dormant follicles to transition into their active anagen growth phase."
</blockquote>

<h2>How to Maximize Nutrient Absorption</h2>
<ul>
    <li>Warm 4-6 drops of HairGlow Oil between your palms to activate the botanical extracts.</li>
    <li>Gently massage into your scalp using circular fingertip motions for 5 minutes.</li>
    <li>Leave in for at least 2 hours or overnight before washing with a mild sulfate-free shampoo.</li>
</ul>

<p>Experience the botanical difference by incorporating natural scalp oiling into your weekly self-care routine 2 to 3 times every week.</p>"""
    },
    {
        'title': 'The Ultimate Step-by-Step Scalp Oiling Routine for Faster Growth',
        'slug': 'the-ultimate-step-by-step-scalp-oil-routine-for-faster-growth',
        'category': 'guides',
        'author': 'HairGlow Specialist',
        'read_time': 4,
        'image': 'blog/blog_2.png',
        'is_published': True,
        'is_featured': True,
        'excerpt': 'Master the art of scalp massage and overnight oiling to boost blood flow, prevent breakage, and double your hair\'s natural shine.',
        'content': """<p class="lead">Oiling is not just a hair care step; it is a therapeutic scalp ritual. Done correctly, it can significantly reduce hair fall, soothe dry flakes, and accelerate natural hair density in as little as 4 to 6 weeks.</p>

<h2>Step 1: Prep & Detangle Gently</h2>
<p>Before applying any oil, always use a wide-tooth wooden comb to gently detangle your hair. This loosens debris on the scalp, improves oil distribution, and prevents snapping delicate strands during massage.</p>

<h2>Step 2: Section Your Hair & Warm the Oil</h2>
<p>Divide your hair into four manageable quadrants. Warm a dropper of HairGlow Oil between your fingertips. Warming the oil thins its consistency, allowing deeper absorption into hair pores and cuticle layers.</p>

<h2>Step 3: The 5-Minute Inversion Technique</h2>
<p>Using gentle, circular pressure with the pads of your fingers, massage your scalp from the nape of your neck towards the crown. This ancient technique stimulates blood flow directly to oxygen-starved follicles.</p>

<blockquote>
Pro Tip: Avoid scratching with fingernails or rubbing aggressively, as high friction can cause traction stress and breakage.
</blockquote>

<h2>Step 4: Steam or Wrap with a Warm Towel</h2>
<p>Wrap your hair in a warm, damp microfiber towel for 15-20 minutes. The gentle heat opens cuticles and amplifies nutrient absorption right down to the root bulb.</p>

<h2>Step 5: Rinse Gently with Sulfate-Free Cleanser</h2>
<p>Wash with a mild, sulfate-free cleanser. You will notice immediately smoother hair texture, enhanced natural luster, and zero greasy residue.</p>"""
    },
    {
        'title': 'Why You Are Experiencing Hair Fall & How to Stop It Naturally',
        'slug': 'why-you-are-experiencing-hair-fall-and-how-to-stop-it-naturally',
        'category': 'hair_care',
        'author': 'HairGlow Wellness Team',
        'read_time': 6,
        'image': 'blog/blog_3.png',
        'is_published': True,
        'is_featured': True,
        'excerpt': 'Understand the root causes of seasonal shedding, stress-induced hair thinning, and how a targeted natural scalp regimen restores fullness.',
        'content': """<p class="lead">Losing 50 to 100 strands a day is completely normal, but excessive thinning and a widening parting line often signal that your scalp ecosystem is out of balance. Here is what is really happening and how to fix it.</p>

<h2>Common Causes of Sudden Hair Shedding</h2>
<p>Hair loss rarely has a single cause. It is usually a combination of external environmental factors and internal stressors:</p>
<ul>
    <li><strong>Hard Water & Sulfates:</strong> Mineral deposits and harsh chemical sulfates clog follicle pores, choking new hair growth.</li>
    <li><strong>Stress & Hormonal Spikes:</strong> High cortisol pushes hair prematurely into the telogen (shedding) resting phase.</li>
    <li><strong>Scalp Barrier Damage:</strong> A compromised scalp moisture barrier weakens the structural anchor of hair roots.</li>
</ul>

<h2>The 3-Pillar Natural Recovery Strategy</h2>

<h3>1. Deep Scalp Detox & Bio-Nutrients</h3>
<p>Feed your hair follicles with bio-active antioxidants and essential fatty acids (Omega 3, 6, and 9) that neutralize free radicals and calm scalp inflammation.</p>

<h3>2. Minimize High-Heat Styling</h3>
<p>Give your hair a break from high-heat blow drying and flat irons for at least 2 to 3 weeks while undergoing intensive botanical oil treatment.</p>

<h3>3. Stay Consistent with Your Regimen</h3>
<p>Hair growth cycles require patience. Applying HairGlow natural oil 2 to 3 times weekly for 30 to 45 days yields visible baby hair growth and significant reduction in breakage.</p>

<blockquote>
"True hair transformation does not happen overnight, but with clean, chemical-free ingredients and steady routine, your hair will regain its natural fullness and bounce."
</blockquote>"""
    }
]

for d in posts_data:
    post, created = BlogPost.objects.update_or_create(
        slug=d['slug'],
        defaults=d
    )
    print(f"{'Created' if created else 'Updated'}: {post.title} (slug: {post.slug})")

print(f"Total BlogPost count: {BlogPost.objects.count()}")
