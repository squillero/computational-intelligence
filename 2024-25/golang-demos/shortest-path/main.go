// Copyright © 2024 Giovanni Squillero <giovanni.squillero@polito.it>
// https://github.com/squillero/computational-intelligence
// Free under certain conditions — see the license for details.

package main

import (
	"demo-sp/graph"
	"demo-sp/randy"
	"demo-sp/solvers"
	"demo-sp/viz"
	"flag"
	"log"
	"log/slog"
	"math/rand/v2"
	"time"
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
	seed := flag.Uint64("r", 42, "Random seed")
	numNodes := flag.Int("n", 10, "Number of nodes")
	edgeProbability := flag.Float64("e", .5, "Edge probability")
	flag.Parse()
	if *verbose {
		slog.SetLogLoggerLevel(slog.LevelDebug)
	}
	if *seed == 0 {
		randy.R = rand.New(rand.NewPCG(uint64(float64(*numNodes) / *edgeProbability),
			uint64(time.Now().UTC().UnixNano())))
	} else {
		randy.R = rand.New(rand.NewPCG(*seed, uint64(float64(*numNodes) / *edgeProbability)))
	}

	slog.Debug("Computational Intelligence 🐹 2024/25!")
	slog.Debug("Using random", "seed", *seed)

	// all passed by reference...
	feed := make(chan interface{}, 1000)
	graph := &graph.Graph{CanvasSize: CanvasSize}
	graph.Initialize(*numNodes, *edgeProbability)

	go func() {
		for n1 := 0; n1 < *numNodes; n1 += 1 {
			feed <- viz.ColoredCircle{Color: viz.ColorMidnightBlue, Center: graph.Nodes[n1], Radius: 5}
			for n2 := n1 + 1; n2 < *numNodes; n2 += 1 {
				if graph.Edges[n1][n2] > 0 {
					feed <- viz.ColoredPolyline{Color: viz.ColorMidnightBlue,
						Polyline: viz.Polyline{Points: []viz.Point{graph.Nodes[n1], graph.Nodes[n2]}}}
				}
			}
		}
	}()

	//go func() {
	//	tag++
	//	solvers.GreedyRandom(graph, feed, tag)
	//}()

	//go func() {
	//	tag++
	//	solvers.GreedyLazy(graph, feed, tag)
	//}()

	//go func() {
	//	tag++
	//	solvers.GreedyInformed(graph, feed, tag)
	//}()

	go func() {
		var tag int32 = 0
		known := make([]int, len(graph.Nodes))
		for s := 0; s < len(graph.Nodes); s++ {
			known[s] = s
		}
		solvers.BranchNBound(graph, feed, tag, known)
	}()

	//go func() {
	//	var tag int32 = 0
	//	known := solvers.GreedyRandom(graph, feed, tag)
	//	solvers.BranchNBound(graph, feed, tag, known)
	//}()

	//go func() {
	//	var tag int32 = 1
	//	known := solvers.GreedyLazy(graph, feed, tag)
	//	solvers.BranchNBound(graph, feed, tag, known)
	//}()

	//go func() {
	//	var tag int32 = 2
	//	known := solvers.GreedyInformed(graph, feed, tag)
	//	solvers.BranchNBound(graph, feed, tag, known)
	//}()

	go solvers.AStarSearch(graph, feed, 1)
	go solvers.GreedySearch(graph, feed, 2)
	go solvers.DepthFirstSearch(graph, feed, 3)
	go solvers.BreadthFirstSearch(graph, feed, 4)
	go solvers.UniformCostSearch(graph, feed, 5)

	viz.Run(feed, "Computational Intelligence 🐹 2024/25", CanvasSize, WindowSize)
	//britishMuseum(graph)
}
