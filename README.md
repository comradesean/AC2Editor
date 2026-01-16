# AC2 uPlay Unlocker

A tool for unlocking DLC and uPlay rewards in Assassin's Creed II save files. Supports both PC and PS3 OPTIONS files.

## Usage

```bash
python ac2_uplay_unlocker.py <OPTIONS_FILE>
```

Examples:
```bash
python ac2_uplay_unlocker.py OPTIONS        # Auto-detect format
python ac2_uplay_unlocker.py OPTIONS.PC     # PC format
python ac2_uplay_unlocker.py OPTIONS.PS3    # PS3 format
```

## Controls

| Key | Action |
|-----|--------|
| `↑`/`↓` or `j`/`k` | Navigate |
| `Space` or `Enter` | Toggle selected unlock |
| `A` | Enable all unlocks |
| `N` | Disable all unlocks |
| `S` | Save changes |
| `Q` or `Esc` | Quit |

## Supported Unlocks

### Templar Lairs (Exclusive Maps)
| Unlock | Description |
|--------|-------------|
| Palazzo Medici | "Home Invasion" |
| Santa Maria Dei Frari | "Over Beams, Under Stone" |
| Arsenal Shipyard | "Shipwrecked" |

### uPlay Rewards
| Unlock | Description |
|--------|-------------|
| Additional Throwing Knives | Increases knife capacity |
| Altaïr Outfit | Classic Altaïr costume |
| Auditore Family Crypt | "Paying Respects" - Exclusive map |

### Promotional Content
| Unlock | Description |
|--------|-------------|
| Bonus Skin | Verizon promotion exclusive |

### PSP Bloodlines Connectivity Weapons
Unlocks weapons from AC: Bloodlines (PSP) save data transfer:

| Weapon |
|--------|
| Maria Thorpe's Longsword |
| Fredrick's Hammer |
| Mace of the Bull |
| Dark Oracle's Bone Dagger |
| Twin's Rapier |
| Bouchart's Blade |

## Platform Differences

### PC Format
- No header or checksum
- Direct read/write of unlock values
- File typically named `OPTIONS` in save directory

### PS3 Format
- 8-byte header: size (4 bytes, big-endian) + CRC32 (4 bytes, big-endian)
- CRC32 parameters:
  - Polynomial: `0x04C11DB7`
  - Initial: `0x00000000`
  - XOR Out: `0x1BF3278A`
  - Reflect Input/Output: Yes
- Requires re-signing with Bruteforce Save Data or similar tool after editing

## Technical Details

### Unlock Structure (Type 0x0E)
Standard boolean unlocks use an 18-byte structure:
```
0E 00 00 00 [HASH:4] 00 00 00 00 00 00 00 00 0B [VALUE]
```
- `0E 00 00 00` - Type identifier (little-endian)
- `[HASH:4]` - 4-byte hash identifying the unlock (little-endian)
- `00...00` - 8 bytes padding
- `0B` - Marker byte
- `[VALUE]` - `00` = locked, `01` = unlocked

### PSP Weapons Structure (Type 0x17)
The Bloodlines weapons use a dynamic boolean array:
```
17 00 00 00 [HASH:4] 00 00 00 00 06 00 17 00 0B 06 00 00 00 [6 BOOLS]
```
- `17 00 00 00` - Type identifier
- `[HASH:4]` - Hash `0xD92D49F7`
- 4-byte counter after `0B` marker indicates 6 boolean values
- Each weapon is a single byte: `00` = locked, `01` = unlocked

### Known Hashes
| Hash | Unlock |
|------|--------|
| `0x41027E09` | Palazzo Medici |
| `0x788F42CC` | Santa Maria Dei Frari |
| `0x6FF4568F` | Arsenal Shipyard |
| `0x1854EC5A` | Bonus Skin |
| `0xC25CE923` | Additional Throwing Knives |
| `0x196CAF1F` | Altaïr Outfit |
| `0x55BEEF7D` | Auditore Family Crypt |
| `0xD92D49F7` | PSP Bloodlines Weapons (array) |

## PS3 Save Editing Workflow

1. Decrypt save with Bruteforce Save Data or PFDTool
2. Run this tool on the OPTIONS file
3. Enable desired unlocks and save
4. Re-sign/re-encrypt save with Bruteforce Save Data

## Requirements

- Python 3.6+
- No external dependencies (curses is optional for enhanced UI)

## License

Public domain - Use freely for personal save editing.
