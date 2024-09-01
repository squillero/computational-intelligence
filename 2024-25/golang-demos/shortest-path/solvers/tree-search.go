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

func DepthFirstSearch(graph *graph.Graph, feed chan<- interface{}, tag int32) []int {
	return treeSearch(graph, feed, tag, "DFS", &Lifo{})
}

func BreadthFirstSearch(graph *graph.Graph, feed chan<- interface{}, tag int32) []int {
	return treeSearch(graph, feed, tag, "BFS", &Fifo{})
}

func UniformCostSearch(graph *graph.Graph, feed chan<- interface{}, tag int32) []int {
	return treeSearch(graph, feed, tag, "UCS",
		&Hpfo{
			p: func(path []int) float64 {
				return graph.PathLength(path)
			},
		})
}

func GreedySearch(graph *graph.Graph, feed chan<- interface{}, tag int32) []int {
	return treeSearch(graph, feed, tag, "Greedy",
		&Hpfo{
			p: func(path []int) float64 {
				return graph.Distance(path[len(path)-1], len(graph.Nodes)-1)
			},
		})
}

func AStarSearch(graph *graph.Graph, feed chan<- interface{}, tag int32) []int {
	return treeSearch(graph, feed, tag, "A*",
		&Hpfo{
			p: func(path []int) float64 {
				return graph.PathLength(path) + graph.Distance(path[len(path)-1], len(graph.Nodes)-1)
			},
		})
}

func treeSearch(graph *graph.Graph, feed chan<- interface{}, tag int32, name string, frontier Queue) []int {
	pp := message.NewPrinter(language.English)

	//check := make(map[string]int)

	frontier.Enqueue([]int{0})
	steps := 0
	for !frontier.Empty() {
		//slog.Debug("TS", "frontier", frontier)
		path := frontier.Dequeue()
		//check[fmt.Sprint(path)]++
		//if check[fmt.Sprint(path)] > 1 {
		//	log.Fatalf("Panik: %v", path)
		//}
		//slog.Debug("TS", "path", path, "len", graph.PathLength(path))
		graph.DrawPath(feed, path, tag)

		if path[len(path)-1] == len(graph.Nodes)-1 {
			feed <- viz.TaggedText{Tag: tag, Text: pp.Sprintf("%s: %.2f (%d) — Completed in %d steps", name,
				graph.PathLength(path), len(path)-1, steps)}
			return path
		} else {
			feed <- viz.TaggedText{Tag: tag, Text: pp.Sprintf("%s: %.2f (%d)", name,
				graph.PathLength(path), len(path)-1)}
		}

		for _, node := range graph.Neighbors(path[len(path)-1]) {
			if in(path, node) {
				continue
			}
			steps++
			new_path := make([]int, len(path)+1)
			copy(new_path, path)
			new_path[len(path)] = node
			frontier.Enqueue(new_path)
		}
	}
	return nil
}
