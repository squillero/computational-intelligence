// Copyright © 2024 Giovanni Squillero <giovanni.squillero@polito.it>
// https://github.com/squillero/computational-intelligence
// Free under certain conditions — see the license for details.

package solvers

import (
	"container/heap"
)

type Queue interface {
	Enqueue(path []int)
	Dequeue() []int
	Empty() bool
}

// Last In - First Out (a Stack)

type Lifo struct {
	data [][]int
}

func (l *Lifo) Empty() bool {
	return len(l.data) == 0
}
func (l *Lifo) Enqueue(path []int) {
	l.data = append(l.data, path)
}

func (l *Lifo) Dequeue() []int {
	d := l.data[len(l.data)-1]
	l.data = l.data[:len(l.data)-1]
	return d
}

// First In - First Out (an English Queue)

type Fifo struct {
	data [][]int
}

func (f *Fifo) Empty() bool {
	return len(f.data) == 0
}
func (f *Fifo) Enqueue(path []int) {
	f.data = append(f.data, path)
}

func (f *Fifo) Dequeue() []int {
	d := f.data[0]
	f.data = f.data[1:len(f.data)]
	return d
}

// Highest Priority First Out (emergency room)

type item struct {
	path     []int
	priority float64
}
type Hpfo struct {
	data []item
	p    func(path []int) float64
}

func (h *Hpfo) Len() int           { return len(h.data) }
func (h *Hpfo) Less(i, j int) bool { return h.data[i].priority < h.data[j].priority }
func (h *Hpfo) Swap(i, j int)      { h.data[i], h.data[j] = h.data[j], h.data[i] }

func (h *Hpfo) Push(x any) {
	h.data = append(h.data, x.(item))
}

func (h *Hpfo) Pop() any {
	e := h.data[len(h.data)-1]
	h.data = h.data[:len(h.data)-1]
	return e
}

func (h *Hpfo) Empty() bool {
	return h.Len() == 0
}
func (h *Hpfo) Enqueue(path []int) {
	heap.Push(h, item{path: path, priority: h.p(path)})
}
func (h *Hpfo) Dequeue() []int {
	return heap.Pop(h).(item).path
}
