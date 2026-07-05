import os
import json

configs_dir = 'configs'
index = {}
games_list = []

if os.path.exists(configs_dir):
    for game_id in sorted(os.listdir(configs_dir)):
        game_path = os.path.join(configs_dir, game_id)
        if os.path.isdir(game_path):
            files = [f for f in os.listdir(game_path) if f.endswith('.json')]
            if not files:
                continue

            # Fallback display name
            display_name = game_id.replace('_', ' ').title()
            steam_id = None
            community_image = None
            files_info = []
            adreno_count = 0
            mali_count = 0
            
            # Sort files by name to ensure deterministic initial display_name
            for filename in sorted(files):
                try:
                    with open(os.path.join(game_path, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        meta = data.get('meta', {})
                        
                        # Prefer name from metadata
                        gname = meta.get('game_name')
                        if gname:
                            display_name = gname
                            
                        if not steam_id:
                            steam_id = meta.get('steam_id', None)
                        if not community_image:
                            community_image = meta.get('community_image', None)
                        
                        device = meta.get('device', {})
                        mfr = str(device.get('manufacturer', '')).capitalize()
                        model = str(device.get('model', ''))
                        gpu = device.get('gpu', 'Unknown GPU')
                        ram = device.get('ram', '')
                        storage = device.get('storage', '')
                        notes = meta.get('notes', '')
                        config_title = meta.get('config_title', '')
                        
                        # GPU Badge Logic
                        gpu_lower = gpu.lower()
                        if 'adreno' in gpu_lower:
                            adreno_count += 1
                        elif 'mali' in gpu_lower or 'immortalis' in gpu_lower:
                            mali_count += 1

                        # Force timestamp to int for stable sorting
                        try:
                            ts = int(meta.get('timestamp', 0))
                        except (ValueError, TypeError):
                            ts = 0

                        files_info.append({
                            "filename": filename,
                            "device_model": f"{mfr} {model}".strip() or "Unknown Device",
                            "gpu": gpu,
                            "ram": ram,
                            "storage": storage,
                            "notes": notes,
                            "config_title": config_title,
                            "timestamp": ts
                        })
                except Exception:
                    files_info.append({"filename": filename, "timestamp": 0})

            games_list.append({
                "id": game_id,
                "name": display_name,
                "steam_id": steam_id,
                "community_image": community_image,
                "config_count": len(files_info),
                "adreno_count": adreno_count,
                "mali_count": mali_count
            })

            # Sort configs by newest first
            index[game_id] = sorted(files_info, key=lambda x: x.get('timestamp', 0), reverse=True)

# Write index with pretty print for better Git diffs
with open('index.json', 'w', encoding='utf-8') as f:
    json.dump(index, f, indent=2, ensure_ascii=False)

# Sort games list case-insensitively
with open('games.json', 'w', encoding='utf-8') as f:
    json.dump(sorted(games_list, key=lambda x: x['name'].lower()), f, indent=2, ensure_ascii=False)
