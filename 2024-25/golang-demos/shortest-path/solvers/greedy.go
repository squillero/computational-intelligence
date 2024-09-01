// Copyright © 2024 Giovanni Squillero <giovanni.squillero@polito.it>
// https://github.com/squillero/computational-intelligence
// Free under certain conditions — see the license for details.

package solvers

import (
	"demo-sp/graph"
	"demo-sp/randy"
	"demo-sp/viz"
	"golang.org/x/text/language"
	"golang.org/x/text/message"
)

type greedyStatus struct {
	graph   *graph.Graph
	feed    chan<- interface{}
	tag     int32
	current []int
	order   []int
	visited []bool
	backs   int32
	pp      *message.Printer
}

func GreedyRandom(graph *graph.Graph, feed chan<- interface{}, tag int32) []int {
	feed <- viz.TaggedText{Tag: tag, Text: "Greedy Random"}
	status := &greedyStatus{
		graph:   graph,
		feed:    feed,
		tag:     tag,
		current: make([]int, 1, len(graph.Nodes)), // 1 element, set cap to nNodes
		order:   randy.R.Perm(len(graph.Nodes)),   // nNodes elems
		visited: make([]bool, len(graph.Nodes)),
		backs:   0,
		pp:      message.NewPrinter(language.English),
	}

	status.current[0] = 0
	greedyStep(status)
	var bt string
	if status.backs != 1 {
		bt = "s"
	}
	status.graph.DrawPath(status.feed, status.current, status.tag)
	status.feed <- viz.TaggedText{Tag: status.tag, Text: status.pp.Sprintf("Greedy (pure random): %.2f (%d) — Completed with %d backtrack%s",
		status.graph.PathLength(status.current), len(status.current)-1, status.backs, bt)}
	return status.current
}

func GreedyInformed(graph *graph.Graph, feed chan<- interface{}, tag int32) []int {
	feed <- viz.TaggedText{Tag: tag, Text: "Greedy Informed"}
	status := &greedyStatus{
		graph:   graph,
		feed:    feed,
		tag:     tag,
		current: make([]int, 1, len(graph.Nodes)), // 1 element, set cap to nNodes
		visited: make([]bool, len(graph.Nodes)),
		backs:   0,
		pp:      message.NewPrinter(language.English),
	}
	status.order = append(status.order, len(status.graph.Nodes)-1)
	for _, n := range status.graph.NodesSorted(len(status.graph.Nodes) - 1) {
		status.order = append(status.order, n)
	}
	status.current[0] = 0
	greedyStep(status)
	var bt string
	if status.backs != 1 {
		bt = "s"
	}
	status.graph.DrawPath(status.feed, status.current, status.tag)
	status.feed <- viz.TaggedText{Tag: status.tag, Text: status.pp.Sprintf("Greedy (informed): %.2f (%d) — Completed with %d backtrack%s",
		status.graph.PathLength(status.current), len(status.current)-1, status.backs, bt)}

	return status.current
}

func GreedyLazy(graph *graph.Graph, feed chan<- interface{}, tag int32) []int {
	feed <- viz.TaggedText{Tag: tag, Text: "Greedy Lazy"}
	status := &greedyStatus{
		graph:   graph,
		feed:    feed,
		tag:     tag,
		order:   make([]int, 0),
		current: make([]int, 1, len(graph.Nodes)), // 1 element, set cap to nNodes
		visited: make([]bool, len(graph.Nodes)),
		backs:   0,
		pp:      message.NewPrinter(language.English),
	}

	status.current[0] = 0
	greedyStep(status)
	var bt string
	if status.backs != 1 {
		bt = "s"
	}
	status.graph.DrawPath(status.feed, status.current, status.tag)
	status.feed <- viz.TaggedText{Tag: status.tag, Text: status.pp.Sprintf("Greedy (lazy): %.2f (%d) — Completed with %d backtrack%s",
		status.graph.PathLength(status.current), len(status.current)-1, status.backs, bt)}

	return status.current
}

func greedyStep(s *greedyStatus) bool {
	last := s.current[len(s.current)-1]
	if last == len(s.graph.Nodes)-1 {
		return true
	}
	// neighbors...
	var order []int
	if len(s.order) > 0 {
		order = s.order
	} else {
		order = make([]int, len(s.graph.NodesSorted(last)))
		copy(order, s.graph.NodesSorted(last))
	}
	neighbors := make([]int, 0, len(s.graph.Nodes))
	for _, n := range order {
		if s.graph.Edges[last][n] > 0 && !s.visited[n] {
			neighbors = append(neighbors, n)
		}
	}
	for _, n := range neighbors {
		if !in(s.current, n) {
			s.current = append(s.current, n)
			if greedyStep(s) {
				return true
			}
			s.backs++
			s.visited[last] = true
			s.current = s.current[:len(s.current)-1]
		}
	}
	return false
}
