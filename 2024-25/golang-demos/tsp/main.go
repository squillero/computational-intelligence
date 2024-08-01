// Copyright © 2024 Giovanni Squillero <giovanni.squillero@polito.it>
// https://github.com/squillero/computational-intelligence
// Free under certain conditions — see the license for details.

package main

import (
	"math/rand"
)

type Dot struct {
	x, y float32
}
type Polygon []Dot

// Game implements ebiten.Game interface.
type Game struct {
	feed   chan Polygon
	cities []Dot
	db     []Polygon
}

func createFeed(c chan Polygon) {
	for {
		//time.Sleep(10 * time.Millisecond)
		var p Polygon
		for np := 3 + rand.Intn(10); np > 0; np -= 1 {
			p = append(p, Dot{x: 1000 * rand.Float32(), y: 1000 * rand.Float32()})
		}
		c <- p
	}
}

func main() {
	var cities []Dot
	for t := 0; t < 50; t += 1 {
		cities = append(cities, Dot{x: 1000 * rand.Float32(), y: 1000 * rand.Float32()})
	}

	game := &Game{feed: make(chan Polygon), cities: cities}
	// Specify the window size as you like. Here, a doubled size is specified.

	go createFeed(game.feed)
	startVisualizer(game)
}
