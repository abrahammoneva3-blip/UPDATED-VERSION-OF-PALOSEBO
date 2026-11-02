# PALOSEBO: FIESTA CLIMB

A 2D pixel-art arcade game based on the Filipino fiesta game **palosebo** (climbing a greased bamboo pole).
Two players race up twin bamboo poles - balance, manage stamina and grab the fiesta flag first!

Everything is drawn and synthesised by the code itself (sprites, backgrounds, sound effects and music),
so the game is **100% offline** and uses **no copyrighted assets**.

## Run it

1. Install Python 3.8+ (https://www.python.org/downloads/).
2. Install Pygame:  `pip install pygame`
3. In this folder run:  `python main.py`  (or open the folder in VS Code and press Run).

The first launch generates the sound files into `assets/sounds/` (already included, so it starts instantly).
Progress is stored in `data/save.json`.

## Controls

| | Player 1 (RIGHT pole) | Player 2 (LEFT pole) |
|---|---|---|
| Climb up / slide down | `W` / `S` | `UP` / `DOWN` |
| Balance left / right | `A` / `D` | `LEFT` / `RIGHT` |

Both players can hold keys at the same time. Menus: `W/A/S/D` or arrow keys + `ENTER` (mouse works too).
`ESC` = pause, `F11` = fullscreen. In **Time Attack** and **Practice** either key set controls the single climber.
Practice mode: `1`-`5` trigger Wind, Rain, Gust, Confetti and Cheer so you can learn to handle them.

> Tip: some cheap keyboards can't register many keys at once ("ghosting"). If a key seems to be ignored while
> both players climb, try another keyboard or a different key combination.

## How to play

* **Climb** with the up key. Climbing drains **stamina**; when it runs low you slow down. Let go to rest - but the
  pole is greased, so you slide down a little while resting. Good pacing beats button-mashing.
* **Balance**: the pole sways and your balance meter drifts. Tap left/right to keep the marker in the green.
  In the yellow/red zone you climb slower; stay in the red too long and you slip down a bit (never all the way to the ground).
* **Events**: Wind, Rain (slippery), Gusts, plus harmless Fiesta Cheer and Confetti.
* First to grab the **flag** wins coins: `WIN 100`, `FAST CLIMB +25`, `PERFECT BALANCE +25`.

## Modes

* **Two Player** - local race. **Time Attack** - one climber vs the clock (best times are saved per stage).
* **Practice** - no opponent, trigger events with 1-5. **Play** - quick-start a Two Player match on your last stage.

## Content

* 5 stages: Barangay, Provincial, Beach, Mountain and Grand Fiesta (win a stage to unlock the next).
* 6 characters (Fiesta Kid, Student, Farmer, Fisherman, Barangay Athlete, Fiesta Champion) - **cosmetic only**,
  every character plays exactly the same.
* Shop (spend coins): characters, hats, outfits, accessories, flag designs, bamboo designs and sky themes.
  Equip hats/outfits/accessories per player in **Characters**; flags, bamboo and skies are equipped in the Shop.

## Project structure

```
main.py             entry point                 app.py           window, scaling, scene stack, fades
game.py             the match (PlayScene)       player.py        climbing, stamina, balance, slipping
bamboo.py           poles, sway, flags          camera.py        smart camera (keeps both players in view)
effects.py          particles, random events, crowd speech bubbles
backgrounds.py      5 procedural fiesta stages  sprites.py       procedural character sprites
menu.py             main menu, stage select, settings, pause
character_select.py shop.py victory.py          catalog.py       all characters / items / stages
sound.py            synthesised SFX + music     save_system.py   local JSON save (data/save.json)
hud.py ui.py gfx.py pixelfont.py settings.py    HUD, UI toolkit, pixel helpers, built-in font, constants
```

Gameplay tuning (speeds, stamina, balance, coin rewards) lives in `settings.py`.
Delete `data/save.json` (or use Settings > Reset Save Data) to start fresh.
