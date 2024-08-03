// Copyright © 2024 Giovanni Squillero <giovanni.squillero@polito.it>
// https://github.com/squillero/computational-intelligence
// Free under certain conditions — see the license for details.

package main

import (
	"demo-sp/viz"
	"flag"
	"log"
	"log/slog"
)

const (
	CanvasSize int = 1000
	WindowSize int = 800
)

func main() {
	log.SetPrefix("CI24 ") // 🐁
	log.SetFlags(log.Ldate | log.Ltime | log.Lmicroseconds | log.Lmsgprefix | log.LUTC)

	// command line arguments
	verbose := flag.Bool("v", false, "Verbose operations")
	flag.Parse()
	if *verbose {
		slog.SetLogLoggerLevel(slog.LevelDebug)
	}
	slog.Debug("This is Computational Intelligence 🐹 2024/25!")

	// Create problem
	numVertexes := 50
	edgeDensity := 0.01

	// all passed by reference...
	feed := make(chan interface{}, numVertexes)
	graph := &Graph{canvasSize: CanvasSize}
	graph.initialize(numVertexes, edgeDensity)

	go func() {
		for _, c := range graph.nodes {
			feed <- viz.ColoredCircle{Color: viz.ColorBabyPink, Center: c, Radius: 3}
		}
		for n1 := 0; n1 < numVertexes; n1 += 1 {
			for n2 := n1 + 1; n2 < numVertexes; n2 += 1 {
				if graph.edges[n1][n2] > 0 {
					feed <- viz.ColoredPolyline{Color: viz.ColorBabyPink,
						Polyline: viz.Polyline{Points: []viz.Point{graph.nodes[n1], graph.nodes[n2]}}}
				}
			}
		}
	}()

	go britishMuseum(graph, feed, 0)
	go britishMuseum(graph, feed, 1)
	go britishMuseum(graph, feed, 2)
	go britishMuseum(graph, feed, 3)

	go func() {
		feed <- viz.TaggedText{Tag: 0, Text: "British Museum Algorithm"}
		feed <- viz.TaggedText{Tag: 1, Text: "British Museum Algorithm"}
		feed <- viz.TaggedText{Tag: 2, Text: "British Museum Algorithm"}
		feed <- viz.TaggedText{Tag: 3, Text: "British Museum Algorithm"}
	}()

	viz.Run(feed, "Zap!", CanvasSize, WindowSize)
	//britishMuseum(graph)
}
