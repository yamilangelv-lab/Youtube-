import torch
from diffusers import DiffusionPipeline
torch.set_num_threads(4)
pipe=DiffusionPipeline.from_pretrained("SimianLuo/LCM_Dreamshaper_v7", torch_dtype=torch.float32, safety_checker=None, requires_safety_checker=False); pipe.set_progress_bar_config(disable=True)
BW=", black and white 1940s documentary photograph, heavy film grain, vintage press photo, cinematic lighting, sharp focus, highly detailed"
CO=", cinematic color photograph, cold blue-green tones, shallow depth of field, highly detailed, sharp focus"
L={"shirt_collar":"close-up of a folded white cotton dress shirt on a wooden table, the inside collar where a small label was cut out, loose threads"+BW,
"hair_tweezers":"steel tweezers holding a single strand of dark hair above a glass petri dish on a forensic laboratory bench, macro photography"+CO,
"rotary_phone":"a vintage black bakelite rotary dial telephone with its handset on a wooden desk, 1940s"+BW,
"plaster_museum":"a single white plaster cast of a man's head inside a glass display case in a dim police museum, side view, face in shadow"+CO}
for k,p in L.items():
    for seed in (21,):
        pipe(prompt=p,num_inference_steps=6,guidance_scale=8.0,width=912,height=512,generator=torch.Generator().manual_seed(seed)).images[0].save(f"img/gen/{k}.png"); print("done",k,flush=True)
