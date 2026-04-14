# Holiday Season Calendar - Complete Reference

## Supported Holidays (11 Total)

This document shows when each holiday is active based on the `holiday_season_controller` automation.

**Note:** Veterans Day has been intentionally excluded as it's a remembrance day that would interrupt Thanksgiving decorations in early November.

### 📅 January

- **Jan 1:** New Years Day
- **Jan 2-6:** Christmas (Epiphany extension)
- **Jan 7-31:** None

### 💕 February

- **Feb 1-6:** None
- **Feb 7-14:** Valentines Day (week before through day of)
- **Feb 15-28:** None

### 🍀 March

- **Mar 1-9:** None
- **Mar 10-17:** St. Patrick's Day (week before through day of)
- **Mar 18-31:** Easter season (if Ash Wednesday starts)

### 🐰 April

- **Apr 1-27:** Easter season (Ash Wednesday through Easter Sunday)
- **Apr 28-30:** Cinco de Mayo (week before starts)

### 🌮 May

- **May 1-5:** Cinco de Mayo (through day of)
- **May 6-17:** None
- **May 18-31:** Memorial Day (week before through last Monday)

### 🎆 June

- **Jun 1-26:** None
- **Jun 27-30:** Independence Day (week before starts)

### 🇺🇸 July

- **Jul 1-11:** Independence Day (week before through week after)
- **Jul 12-31:** None

### 🏖️ August

- **Aug 1-24:** None
- **Aug 25-31:** Labor Day (week before starts)

### 👔 September

- **Sep 1-7:** Labor Day (through first Monday, approximately)
- **Sep 8-30:** None

### 🎃 October

- **Oct 1-31:** Halloween (entire month)

### 🦃 November

- **Nov 1-27:** Thanksgiving (through Thanksgiving Day - 4th Thursday)
- **Nov 28-30:** Christmas (Black Friday starts)

### 🎄 December

- **Dec 1-31:** Christmas (entire month)

## Priority Order (When Overlaps Occur)

The automation evaluates holidays in this order (first match wins):

1. New Years (Jan 1 only)
2. Christmas extension (Jan 2-6)
3. Valentines Day (Feb 7-14)
4. St. Patrick's Day (Mar 10-17)
5. Easter (Ash Wednesday to Easter Sunday - movable, usually Mar-Apr)
6. Cinco de Mayo (Apr 28 - May 5)
7. Memorial Day (Last Monday of May, week before to day of)
8. Independence Day (Jun 27 - Jul 11)
9. Labor Day (First Monday of Sep, week before to day of)
10. Halloween (October 1-31)
11. Thanksgiving (Nov 1 - Thanksgiving Day)
12. Christmas (Black Friday - Dec 31)

## Movable Holidays (Calculated Dates)

### Easter (2025-2030)

- **2025:** April 20 (Ash Wednesday: March 5)
- **2026:** April 5 (Ash Wednesday: February 18)
- **2027:** March 28 (Ash Wednesday: February 10)
- **2028:** April 16 (Ash Wednesday: March 1)
- **2029:** April 1 (Ash Wednesday: February 14)
- **2030:** April 21 (Ash Wednesday: March 6)

### Thanksgiving (2025-2030)

- **2025:** November 27 (4th Thursday)
- **2026:** November 26 (4th Thursday)
- **2027:** November 25 (4th Thursday)
- **2028:** November 23 (4th Thursday)
- **2029:** November 22 (4th Thursday)
- **2030:** November 28 (4th Thursday)

### Memorial Day (2025-2030)

- **2025:** May 26 (Last Monday)
- **2026:** May 25 (Last Monday)
- **2027:** May 31 (Last Monday)
- **2028:** May 29 (Last Monday)
- **2029:** May 28 (Last Monday)
- **2030:** May 27 (Last Monday)

### Labor Day (2025-2030)

- **2025:** September 1 (First Monday)
- **2026:** September 7 (First Monday)
- **2027:** September 6 (First Monday)
- **2028:** September 4 (First Monday)
- **2029:** September 3 (First Monday)
- **2030:** September 2 (First Monday)

## Holiday Duration Philosophy

**Short Holidays (1 week):**

- Valentines Day
- St. Patrick's Day
- Cinco de Mayo
- Veterans Day

**Medium Holidays (2 weeks):**

- Memorial Day
- Independence Day
- Labor Day

**Long Holidays (3-7 weeks):**

- Easter (Lent season: 46 days)
- Thanksgiving (2-3 weeks depending on calendar)

**Full Month Holidays:**

- Halloween (October)
- Christmas (December + first week of January)

## Decoration Planning by Holiday

### Indoor Decorations

Good for: All holidays (can be themed)

### Outdoor Decorations

Best for:

- Halloween (Oct)
- Thanksgiving (Nov)
- Christmas (Nov 28 - Jan 6)
- Independence Day (Jul 4 week)
- Memorial Day (last Mon of May)

### Accent Lighting

Good for:

- Valentines Day (pink/red)
- St. Patrick's Day (green)
- Easter (pastels)
- Independence Day (red/white/blue)
- Halloween (orange/purple)
- Christmas (red/green/white)

## Label Recommendations

Suggested Home Assistant labels to create:

- **New Years** - Gold/silver theme
- **Valentines Day** - Pink/red theme
- **St. Patrick's Day** - Green theme (already exists ✅)
- **Easter** - Pastel theme (already exists ✅)
- **Cinco de Mayo** - Red/green/white theme
- **Memorial Day** - Red/white/blue theme
- **Independence Day** - Red/white/blue theme (already exists ✅)
- **Labor Day** - No theme (usually not decorated)
- **Halloween** - Orange/black theme (already exists ✅)
- **Thanksgiving** - Brown/orange/yellow theme (already exists ✅)
- **Christmas** - Red/green theme (already exists ✅)

**Note:** Veterans Day removed from decoration rotation - it's a remembrance day that would interrupt Thanksgiving decorations.

## Current Status (Nov 10, 2025)

Based on today's date:

- **Active Holiday:** Thanksgiving (Nov 12-27 window)
- **Days until end:** 17 days (until Nov 27)
- **Next Holiday:** Christmas (starts Nov 28 - Black Friday)

## Testing Commands

```bash
# Check current holiday
echo "{{ states('input_select.active_holiday') }}" | \
  docker exec -i home-assistant python -m homeassistant --script check_config

# Force controller to run
# Go to: Developer Tools > Services > automation.trigger
# Select: automation.holiday_season_controller
```

## Manual Override

You can manually change `input_select.active_holiday` in the UI:

- Settings > Devices & Services > Helpers
- Find "Active Holiday"
- Select any holiday

**Note:** The automation will revert to calculated value:

- At next midnight (12:01 AM)
- On Home Assistant restart
- After 1 hour (if you change it manually)
