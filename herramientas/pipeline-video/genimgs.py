import torch, os, json
from diffusers import DiffusionPipeline
torch.set_num_threads(4)
P=os.path.dirname(os.path.abspath(__file__))
pipe=DiffusionPipeline.from_pretrained("SimianLuo/LCM_Dreamshaper_v7", torch_dtype=torch.float32); pipe.set_progress_bar_config(disable=True)
BW=", black and white 1940s documentary photograph, heavy film grain, vintage press photo, cinematic lighting, sharp focus, highly detailed"
CO=", cinematic color photograph, cold blue-green tones, shallow depth of field, highly detailed, sharp focus"
L={
"adelaide_street":"1940s Australian city street with an old tram and sandstone buildings, pedestrians in hats seen from far away"+BW,
"beach_evening":"an empty 1940s seaside beach at evening with a low concrete seawall and steps, two tiny distant figures walking, no buildings, no city, calm sea"+BW,
"suit_silhouette":"silhouette of a man in a 1940s suit and fedora hat standing alone on a beach at dusk, seen from behind, face not visible"+BW,
"cigarettes":"close-up of a worn vintage cigarette packet and loose cigarettes on a dark wooden table, no text"+BW,
"pathology_lab":"empty 1940s pathology laboratory with glass bottles, brass microscope, enamel trays, dim window light, no people"+BW,
"poison_bottles":"row of vintage pharmacy glass bottles with blank paper labels on a wooden shelf, dramatic side light"+BW,
"coroner_court":"empty 1940s courtroom interior with wooden benches and a judge's bench, window light, no people"+BW,
"suitcase_counter":"a brown leather suitcase on a 1940s railway luggage counter with a paper tag attached"+BW,
"suitcase_open":"an open vintage leather suitcase with folded shirts, neckties and small tools, top-down view"+BW,
"tie_label":"close-up of the inner lining of an old silk necktie with a small blank white fabric label"+BW,
"aged_paper":"blank sheet of old aged yellowed paper texture, stains and creases, top-down, no text, empty",
"book_open":"an old small hardcover poetry book lying open on a dark table, the last page has a torn missing corner, warm lamp light"+BW,
"book_back":"the inside back cover of an old book, blank aged paper, faint pencil smudges, top-down, lamp light, no text"+BW,
"car_night":"a 1940s car parked near the seaside at night, a flashlight beam shining on the back seat, fog"+BW,
"rotary_phone":"close-up of a 1940s black rotary telephone on a wooden table"+BW,
"glenelg_street":"a quiet 1940s seaside suburb street with bungalow houses and palm trees, afternoon"+BW,
"woman_doorway":"silhouette of a young woman in a 1940s dress standing in a house doorway, strong backlight, face not visible"+BW,
"book_inscription":"an old poetry book open to the first page with a faded illegible handwritten inscription"+BW,
"bust_cloth":"a plaster bust covered by a white cloth on a table in a 1940s police station, dim light"+BW,
"detective_office":"1940s police detective office, desk with paper files and a typewriter, cigarette smoke, no people"+BW,
"three_files":"three manila case folders lying on a wooden desk, top-down view, blank covers"+BW,
"teletype":"1940s teletype machine and a closed folder on a desk in a dark office, cold war atmosphere"+BW,
"beach_night_figures":"two distant silhouettes on a beach at night, one man carrying another man on his shoulders, moonlight, far away"+BW,
"cemetery_bw":"old Australian cemetery at dawn with rows of headstones and fog"+BW,
"melbourne_street":"1940s city street, a man in a hat and overcoat walking away from the camera"+BW,
"newspaper":"close-up of a vintage 1940s newspaper page, columns of small blurry text, crumpled"+BW,
"paper_scrap":"macro photograph of a tiny torn scrap of old paper lying on dark wool fabric, blank paper"+BW,
"shirt_collar":"macro of the inside of a white shirt collar with the label cut out, loose threads"+BW,
"university":"sandstone university building with gothic windows on a sunny day, cinematic color photograph, highly detailed",
"exhumation_tent":"white forensic tent over a grave in a cemetery at dawn, investigators in white protective suits seen from behind"+CO,
"dna_lab":"modern DNA sequencing laboratory with computer screens and pipettes, no people"+CO,
"hair_tweezers":"tweezers holding a single hair under a magnifying lens in a forensic lab, macro"+CO,
"plaster_museum":"an old white plaster cast inside a glass museum display case, dim museum, the face in shadow"+CO,
"beach_sunset":"an empty beach with a low concrete seawall at sunset, warm golden light, calm sea, cinematic color photograph, highly detailed",
"ocean_horizon":"calm ocean horizon at dusk, soft clouds, cinematic color photograph, highly detailed",
}
os.makedirs(f"{P}/img/gen",exist_ok=True)
for k,p in L.items():
    fn=f"{P}/img/gen/{k}.png"
    if os.path.exists(fn): continue
    g=torch.Generator().manual_seed(7)
    pipe(prompt=p,num_inference_steps=6,guidance_scale=8.0,width=912,height=512,generator=g).images[0].save(fn)
    print("done",k,flush=True)
print("ALL DONE")
