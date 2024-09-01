// Copyright © 2024 Giovanni Squillero <giovanni.squillero@polito.it>
// https://github.com/squillero/computational-intelligence
// Free under certain conditions — see the license for details.

package solvers

import (
	"demo-sp/graph"
	"demo-sp/viz"
	"golang.org/x/text/language"
	"golang.org/x/text/message"
)

type bnbStatus struct {
	graph   *graph.Graph
	feed    chan<- interface{}
	tag     int32
	current []int
	best    []int
	steps   int32
	pp      *message.Printer
}

func BranchNBound(graph *graph.Graph, feed chan<- interface{}, tag int32, knownSolution []int) []int {
	// British Museum algorithm -- see: https://en.wikipedia.org/wiki/British_Museum_algorithm

	feed <- viz.TaggedText{Tag: tag, Text: "Branch n' Bound"}
	status := &bnbStatus{
		graph:   graph,
		feed:    feed,
		tag:     tag,
		current: make([]int, 1, len(graph.Nodes)), // 1 element, set cap to nNodes
		best:    knownSolution,                    // nNodes elems
		steps:   0,
		pp:      message.NewPrinter(language.English),
	}
	status.current[0] = 0
	status.feed <- viz.TaggedText{Tag: status.tag, Text: status.pp.Sprintf("BnB: %.2f (%d) — Warming up...",
		status.graph.PathLength(status.best), len(status.best)-1)}
	bnbStep(status)
	status.feed <- viz.TaggedText{Tag: status.tag, Text: status.pp.Sprintf("BnB: %.2f (%d) — Completed in %d steps",
		status.graph.PathLength(status.best), len(status.best)-1, status.steps)}
	return status.best
}

func bnbStep(s *bnbStatus) {
	s.steps++
	last := s.current[len(s.current)-1]
	if last == len(s.graph.Nodes)-1 {
		if s.graph.PathLength(s.current) < s.graph.PathLength(s.best) {
			s.best = s.best[:len(s.current)]
			copy(s.best, s.current)
			s.graph.DrawPath(s.feed, s.best, s.tag)
			s.feed <- viz.TaggedText{Tag: s.tag, Text: s.pp.Sprintf("BnB: %.2f (%d)",
				s.graph.PathLength(s.best)-1, len(s.best))}
		}
		return
	} else if s.graph.PathLength(s.current) > s.graph.PathLength(s.best) {
		// bound
		return
	}
	for _, n := range s.graph.Neighbors(last) {
		if !in(s.current, n) {
			s.current = append(s.current, n)
			bnbStep(s)
			s.current = s.current[:len(s.current)-1]
		}
	}
}
