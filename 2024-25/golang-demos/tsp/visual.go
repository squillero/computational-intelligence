// Copyright © 2024 Giovanni Squillero <giovanni.squillero@polito.it>
// https://github.com/squillero/computational-intelligence
// Free under certain conditions — see the license for details.

package main

import (
	"image/color"
	"log"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/vector"
)

// Update proceeds the game state.
// Update is called every tick (1/60 [s] by default).
func (g *Game) Update() error {
	done := false
	for !done {
		select {
		case p := <-g.feed:
			g.db = append(g.db, p)
		default:
			done = true
		}
	}
	return nil
}

// Draw draws the game screen.
// Draw is called every frame (typically 1/60[s] for 60Hz display).
func (g *Game) Draw(screen *ebiten.Image) {
	var p, i int
	for p = 0; p < len(g.db)-1; p += 1 {
		y := uint8(1 + (p*128)/len(g.db))
		for i = 0; i < len(g.db[p])-1; i += 1 {
			vector.StrokeLine(screen, g.db[p][i].x, g.db[p][i].y, g.db[p][i+1].x, g.db[p][i+1].y, 1, color.Gray{Y: y}, false)
		}
		vector.StrokeLine(screen, g.db[p][i].x, g.db[p][i].y, g.db[p][0].x, g.db[p][0].y, 1, color.Gray{Y: y}, false)
	}
	if p < len(g.db) {
		for i = 0; i < len(g.db[p])-1; i += 1 {
			vector.StrokeLine(screen, g.db[p][i].x, g.db[p][i].y, g.db[p][i+1].x, g.db[p][i+1].y, 1, color.Gray{Y: 255}, false)
		}
		vector.StrokeLine(screen, g.db[p][i].x, g.db[p][i].y, g.db[p][0].x, g.db[p][0].y, 1, color.Gray{Y: 255}, false)
	}
	for _, p := range g.cities {
		vector.DrawFilledCircle(screen, p.x, p.y, 5, color.RGBA{0xff, 0, 0, 0}, true)
	}

}

// Layout takes the outside size (e.g., the window size) and returns the (logical) screen size.
// If you don't have to adjust the screen size with the outside size, just return a fixed size.
func (g *Game) Layout(outsideWidth, outsideHeight int) (screenWidth, screenHeight int) {
	return 1000, 1000
}

func startVisualizer(g *Game) {
	ebiten.SetWindowSize(800, 800)
	ebiten.SetWindowTitle("TSP")
	// Call ebiten.RunGame to start your game loop.
	if err := ebiten.RunGame(g); err != nil {
		log.Fatal(err)
	}
}
