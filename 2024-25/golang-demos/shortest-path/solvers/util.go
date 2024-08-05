// Copyright © 2024 Giovanni Squillero <giovanni.squillero@polito.it>
// https://github.com/squillero/computational-intelligence
// Free under certain conditions — see the license for details.

package solvers

func in(path []int, n int) bool {
	for _, p := range path {
		if p == n {
			return true
		}
	}
	return false
}
