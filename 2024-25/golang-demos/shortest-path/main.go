// Copyright © 2024 Giovanni Squillero <giovanni.squillero@polito.it>
// https://github.com/squillero/computational-intelligence
// Free under certain conditions — see the license for details.

package main

import (
	graph2 "demo-sp/graph"
	british_museum "demo-sp/solvers"
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
	slog.Debug("Thisis Computational Intelligence 🐹 2024/25!")

	// Create problem
	numNodes := 100
	edgeDensity := 0.01

	// all passed by reference...
	feed := make(chan interface{}, numNodes)
	graph := &graph2.Graph{CanvasSize: CanvasSize}
	graph.Initialize(numNodes, edgeDensity)

	go func() {
		for n1 := 0; n1 < numNodes; n1 += 1 {
			feed <- viz.ColoredCircle{Color: viz.ColorMidnightBlue, Center: graph.Nodes[n1], Radius: 5}
			for n2 := n1 + 1; n2 < numNodes; n2 += 1 {
				if graph.Edges[n1][n2] > 0 {
					feed <- viz.ColoredPolyline{Color: viz.ColorMidnightBlue,
						Polyline: viz.Polyline{Points: []viz.Point{graph.Nodes[n1], graph.Nodes[n2]}}}
				}
			}
		}
	}()

	//go func() {
	//	for t := range viz.TagColors {
	//		go british_museum.BranchNBound(graph, feed, int32(t))
	//	}
	//}()
	go british_museum.BranchNBound(graph, feed, 0)

	//go func() {
	//	for t := 0; t < viz.MaxTags; t++ {
	//		feed <- viz.TaggedText{Tag: int32(t), Text: "British Museum Algorithm"}
	//	}
	//}()

	viz.Run(feed, "Computational Intelligence 🐹 2024/25", CanvasSize, WindowSize)
	//britishMuseum(graph)
}
