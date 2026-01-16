# Assassin's Creed 2 OPTIONS Mapping Reference

# Platform Base Addresses

| Platform | Base Address | Offset |
|----------|--------------|--------|
| PS3 | `0x0` | 0 |
| PC | `0x220` | +544 bytes |

## Notes

- The PC version has a **+0x220 offset** (544 bytes) compared to PS3
- When converting addresses from PS3 to PC: **PC Address = PS3 Address + 0x220**
- When converting addresses from PC to PS3: **PS3 Address = PC Address - 0x220**

---

#### Language Configuration
| Address Range | Type | Description |
|---------|------|-------------|
| `0x21e`–`0x225` | Audio | Language selection (8 bytes) |

*Refer to language_table for specific language codes*

## General Settings

| Setting | Address | Value Range | Notes |
|---------|---------|-------------|-------|
| **Action Camera Frequency** | `0x2fa` | `0x00` → `0x03` | |
| **SFX Volume** | `0x261` - `0x264` | See volume table below | 4-byte float |
| **Voice Volume** | `0x24c` - `0x24f` | Same pattern as SFX | 4-byte float |
| **Music Volume** | `0x237` - `0x23a` | Same pattern as SFX | 4-byte float |
| **Brightness** | `0x30c` | `0x00` → `0x09` | 10 levels |
| **Blood Toggle** | `0x31e` | Boolean | On/Off |
| **Subtitles Toggle** | `0x1f3` | Boolean | On/Off |

### Volume Mapping (SFX/Voice/Music)
**4-byte float, little-endian**

| Level | Hex Value | Decimal (dB) |
|-------|-----------|--------------|
| 10 | `0x00 00 00 00` | 0.0 (Max) |
| 9 | `0x44 47 6A BF` | -0.916 |
| 8 | `0xF0 16 F8 BF` | -1.938 |
| 7 | `0x46 46 46 C0` | -3.098 |
| 6 | `0xB2 FB 8D C0` | -4.437 |
| 5 | `0xC0 A8 C0 C0` | -6.020 |
| 4 | `0x7C AE FE C0` | -7.958 |
| 3 | `0x39 52 27 C1` | -10.457 |
| 2 | `0x9E AB 5F C1` | -13.979 |
| 1 | `0xFF FF 9F C1` | -19.999 |
| 0 | `0x00 00 C0 C2` | -96.0 (Mute) |

## Controls

### Camera Inversion

| Setting | Address | Type |
|---------|---------|------|
| **3rd Person - Invert Y Look** | `0x2c4` | Boolean |
| **3rd Person - Invert X Look** | `0x2b2` | Boolean |
| **1st Person - Invert Y Look** | `0x2e8` | Boolean |
| **1st Person - Invert X Look** | `0x2d6` | Boolean |

### Look Sensitivity

| Setting | Address | Notes |
|---------|---------|-------|
| **Y Look Sensitivity** | `0x29d` - `0x2a0` | 4-byte float (see table below) |
| **X Look Sensitivity** | `0x288` - `0x28b` | Same pattern as Y sensitivity |

#### Sensitivity Mapping
**4-byte float, little-endian**

| Level | Hex Value | Multiplier |
|-------|-----------|------------|
| 10 (Max) | `0x00 00 00 40` | 2.0x |
| 9 | `0x66 66 E6 3F` | 1.8x |
| 8 | `0xCD CC CC 3F` | 1.6x |
| 7 | `0x33 33 B3 3F` | 1.4x |
| 6 | `0x9A 99 99 3F` | 1.2x |
| 5 (Default) | `0x00 00 80 3F` | 1.0x |
| 4 | `0xCD CC 4C 3F` | 0.8x |
| 3 | `0x33 33 33 3F` | 0.7x |
| 2 | `0x9A 99 19 3F` | 0.6x |
| 1 (Min) | `0x00 00 00 3F` | 0.5x |

**Pattern:**
- Levels 1-4: Increment by 0.1x (0.5 → 0.8)
- Level 5: 1.0x baseline (jump of 0.2)
- Levels 6-10: Increment by 0.2x (1.2 → 2.0)
- **Range:** 0.5x to 2.0x (50% to 200% of base sensitivity)

### Other Controls

| Setting | Address | Values | Notes |
|---------|---------|--------|-------|
| **Flying Machine** | `0x330` | `0x00` = Normal<br>`0x01` = Inverted | |
| **Vibration** | `0x276` | Boolean | On/Off |

## HUD Settings

| Setting | Address | Type |
|---------|---------|------|
| **Health Meter** | `0x342` | Boolean |
| **Controls** | `0x354` | Boolean |
| **Updates** | `0x366` | Boolean |
| **Weapon** | `0x378` | Boolean |
| **SSI** | `0x3c0` | Boolean |
| **Money** | `0x39c` | Boolean |
| **Mini-Map** | `0x38a` | Boolean |

---

### Unlockable Content

#### Templar Lair Unlocks
| Address | Value Change | Description |
|---------|-------------|-------------|
| `0x3D2` | `0x00` → `0x01` | Palazzo Medici - "Home Invasion" |
| `0x3E4` | `0x00` → `0x01` | Santa Maria Dei Frari - "Over Beams, Under Stone" |
| `0x3F6` | `0x00` → `0x01` | Arsenal Shipyard - "Shipwrecked" |

#### uPlay Unlocks
| Address | Value Change | Description |
|---------|-------------|-------------|
| `0x41A` | `0x00` → `0x01` | Bonus Skin (Verizon Promotion) |
| `0x474` | `0x00` → `0x01` | Additional Throwing Knives |
| `0x486` | `0x00` → `0x01` | Altaïr Outfit |
| `0x498` | `0x00` → `0x01` | Uplay Exclusive Map (Auditore Family Crypt) - "Paying Respects" |

#### Assassin's Creed Bloodlines (PSP) Weapon Unlocks
| Address | Value Change | Description |
|---------|-------------|-------------|
| `0x56B` | `0x00` → `0x01` | Maria Thorpe's Longsword |
| `0x56C` | `0x00` → `0x01` | Fredrick's Hammer |
| `0x56D` | `0x00` → `0x01` | Mace of the Bull |
| `0x56E` | `0x00` → `0x01` | Dark Oracle's Bone Dagger |
| `0x56F` | `0x00` → `0x01` | Twin's Rapier |
| `0x570` | `0x00` → `0x01` | Bouchart's Blade |

---

## Technical Notes

### Data Types
- **Boolean**: Single byte (`0x00` = Off, `0x01` = On)
- **Float**: 4-byte IEEE 754 floating point, little-endian format
- **Range**: Single byte with specified min/max values

### Byte Order
All multi-byte values use **little-endian** byte order (least significant byte first).

### Volume Scale
Audio volumes use a logarithmic decibel (dB) scale:
- **0 dB** = Maximum volume (100%)
- **-96 dB** = Effective silence (mute)
- Each step reduces volume non-linearly for perceptual consistency