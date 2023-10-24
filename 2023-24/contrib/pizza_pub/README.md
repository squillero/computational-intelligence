# Pizza pub problem

## Description

A group of friends has to move from a pizzeria to a pub, the friends group is composed of computer engineers(ce), and data scientists(ds).
The vehicle they have to move from one place to the other is a bike with a certain number of seats.
At any moment in either the pizzera or pub the number of data scientists (if any) must be equal or greater to the number of computer engineers.

## Goal

Move everyone from the pizzeria to the pub using the bike

## Solution

The current state of the problem is defined as the number of computer engineers (ce) and data scientists (ds) at the pizzeria, on the bike and at the pub plus the position of the bike.

The position of the bike is necessary since you cannot mount a bike which is elsewhere unless somebody is bringing it to you.

This description of the state considers states where the position of the bike is different as  different states, even though if at least one person is on the bike these two different states can generate the same set of adjacent states. (This may very well be improved in the future).

The solution is found by generating from the initial state the adjacent states and exploring them until a solution is found. The same state is not analyzed twice.
