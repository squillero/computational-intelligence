// Copyright © 2024 Giovanni Squillero <giovanni.squillero@polito.it>
// https://github.com/squillero/computational-intelligence
// Free under certain conditions — see the license for details.

package main

import (
	"demo-sp/viz"
	"math/rand"
)

func britishMuseum(graph *Graph, feed chan<- interface{}, tag int32) {
	cs := float32(graph.canvasSize)
	for {
		var p viz.TaggedPolyline
		p.Tag = tag
		p.Points = make([]viz.Point, 0)
		for np := 3 + rand.Intn(10); np > 0; np -= 1 {
			p.Points = append(p.Points, viz.Point{X: cs * rand.Float32(), Y: cs * rand.Float32()})
		}
		feed <- p
	}
}
