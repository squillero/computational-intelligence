// Copyright © 2024 Giovanni Squillero <giovanni.squillero@polito.it>
// https://github.com/squillero/computational-intelligence
// Free under certain conditions — see the license for details.

package graph

import (
	"demo-sp/randy"
	"demo-sp/viz"
	"math"
	"sort"
)

type Graph struct {
	CanvasSize int
	Nodes      []viz.Point
	Edges      [][]float64
}

func distance(cities []viz.Point, c1 int, c2 int) float64 {
	return math.Sqrt(math.Pow(float64(cities[c1].X-cities[c2].X), 2) + math.Pow(float64(cities[c1].Y-cities[c2].Y), 2))
}

func (g *Graph) Distance(c1 int, c2 int) float64 {
	return distance(g.Nodes, c1, c2)
}

func (g *Graph) Initialize(numNodes int, edgeProbability float64) {

	// Nodes
	g.Nodes = make([]viz.Point, numNodes)
	cs := float32(g.CanvasSize)
	g.Nodes[0] = viz.Point{X: cs * .05, Y: cs * .95}          // source: first node
	g.Nodes[numNodes-1] = viz.Point{X: cs * .95, Y: cs * .05} // destination: last node
	for t := 1; t < numNodes-1; {
		g.Nodes[t] = viz.Point{X: cs * randy.R.Float32(), Y: cs * randy.R.Float32()}
		if g.Distance(t, g.nearest(t)) > float64(cs/5)/float64(numNodes) {
			t++
		}
	}
	// Edges
	g.Edges = make([][]float64, numNodes)
	for i := range g.Edges {
		g.Edges[i] = make([]float64, numNodes)
	}
	// create a safe, yet terribly long path from source to destination
	for c := 0; c < numNodes-1; c++ {
		g.Edges[c][c+1] = g.Distance(c, c+1)
	}
	// add random Edges
	for n0 := 0; n0 < numNodes; n0++ {
		n := g.NodesSorted(n0)
		for t := 0; t < numNodes-1 && (t == 0 || randy.R.Float64() < edgeProbability); t++ {
			g.Edges[n0][n[t]] = distance(g.Nodes, n0, n[t])
			g.Edges[n[t]][n0] = g.Edges[n0][n[t]]
		}
	}
}

func (g *Graph) NodesSorted(v int) []int {
	// return the list of nodes sorted by distance from vertex v
	n := make([]struct {
		v int
		d float64
	}, len(g.Nodes))
	for i := range n {
		n[i].v = i
		n[i].d = g.Distance(v, i)
	}
	sort.Slice(n, func(i, j int) bool {
		return n[i].d < n[j].d
	})
	r := make([]int, len(g.Nodes)-1)
	for i := 1; i < len(g.Nodes); i++ {
		r[i-1] = n[i].v
	}
	return r
}

func (g *Graph) PathLength(path []int) float64 {
	length := 0.0
	for i := 0; i < len(path)-1; i++ {
		length += g.Edges[path[i]][path[i+1]]
	}
	return length
}

func (g *Graph) DrawPath(feed chan<- interface{}, path []int, tag int32) {
	p := make([]viz.Point, len(path))
	for s := 0; s < len(path); s++ {
		p[s] = g.Nodes[path[s]]
	}
	for i := 0; i < len(path)-1; i++ {
		feed <- viz.TaggedVanishingPolyline{Tag: tag, Polyline: viz.Polyline{Points: p}}
	}
}

func (g *Graph) Neighbors(v int) []int {
	r := make([]int, 0)
	for i := 0; i < len(g.Nodes); i++ {
		if g.Edges[v][i] > 0 {
			r = append(r, i)
		}
	}
	return r
}

func (g *Graph) NearestNeighbors(v int) []int {
	r := make([]int, 0)
	for _, i := range g.NodesSorted(v) {
		if g.Edges[v][i] > 0 {
			r = append(r, i)
		}
	}
	return r
}

func (g *Graph) nearest(v int) int {
	var nearest int = 0

	if nearest == v {
		nearest++
	}
	for i := 0; i < len(g.Nodes); i++ {
		if i != v && g.Distance(i, v) < g.Distance(nearest, v) {
			nearest = i
		}
	}
	return nearest
}
