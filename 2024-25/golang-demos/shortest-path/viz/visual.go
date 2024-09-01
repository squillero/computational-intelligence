// Copyright © 2024 Giovanni Squillero <giovanni.squillero@polito.it>
// https://github.com/squillero/computational-intelligence
// Free under certain conditions — see the license for details.

package viz

import (
	"bytes"
	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/examples/resources/fonts"
	"github.com/hajimehoshi/ebiten/v2/text/v2"
	"github.com/hajimehoshi/ebiten/v2/vector"
	"image/color"
	"log"
)

const MaxTags int = 8

var TagColors [MaxTags]color.RGBA = [MaxTags]color.RGBA{
	ColorOrangeRed,
	ColorGold,
	ColorSpringGreen,
	ColorDeepskyBlue,
	ColorDeepPink,
	ColorDarkOliveGreen,
	ColorBlue,
	ColorMidnightBlue,
}

type Point struct {
	X, Y float32
}
type Polyline struct {
	Points []Point
}
type ColoredPolyline struct {
	Color color.RGBA
	Polyline
}
type TaggedPolyline struct {
	Tag int32
	Polyline
}
type TaggedVanishingPolyline TaggedPolyline

type ColoredCircle struct {
	Color  color.RGBA
	Center Point
	Radius float32
}
type TaggedText struct {
	Text        string
	Tag         int32
	drawOptions *text.DrawOptions
}

// vizData implements ebiten.Game interface.
type vizData struct {
	feed                     <-chan interface{}
	playgroundSize           int
	coloredPolylines         []ColoredPolyline
	taggedPolylines          [MaxTags]Polyline
	taggedVanishingPolylines [MaxTags][]Polyline
	taggedTexts              [MaxTags]TaggedText
	coloredCircles           []ColoredCircle
	textFaceSource           *text.GoTextFaceSource
}

// Layout takes the outside size (e.g., the window size) and returns the (logical) screen size.
// If you don't have to adjust the screen size with the outside size, just return a fixed size.
func (data *vizData) Layout(_, _ int) (screenWidth, screenHeight int) {
	return data.playgroundSize, data.playgroundSize
}

// Update the ebiten "game state" (called every 1/60s tick by default)
func (data *vizData) Update() error {
	for done := false; !done; {
		select {
		case f := <-data.feed:
			switch f.(type) {
			case ColoredPolyline:
				data.coloredPolylines = append(data.coloredPolylines, f.(ColoredPolyline))
			case TaggedPolyline:
				data.taggedPolylines[f.(TaggedPolyline).Tag] = Polyline{Points: f.(TaggedPolyline).Points}
			case TaggedVanishingPolyline:
				data.taggedVanishingPolylines[f.(TaggedVanishingPolyline).Tag] = append(data.taggedVanishingPolylines[f.(TaggedVanishingPolyline).Tag],
					Polyline{Points: f.(TaggedVanishingPolyline).Points})
			case ColoredCircle:
				data.coloredCircles = append(data.coloredCircles, f.(ColoredCircle))
			case TaggedText:
				t := f.(TaggedText)
				t.drawOptions = &text.DrawOptions{}
				t.drawOptions.GeoM.Translate(26, 10+float64(t.Tag*20)-10)
				t.drawOptions.ColorScale.ScaleWithColor(color.White)
				data.taggedTexts[f.(TaggedText).Tag] = t
			default:
				log.Fatalf("Unknown message ``%s'' in feed channel", f)
			}
		default:
			done = true
		}
	}
	return nil
}

// Draw draws the game screen.
// Draw is called every frame (typically 1/60[s] for 60Hz display).
func (data *vizData) Draw(screen *ebiten.Image) {
	// static polyline
	for _, l := range data.coloredPolylines {
		drawPolyline(screen, l.Points, 5, l.Color)
	}
	// circles
	for _, c := range data.coloredCircles {
		vector.DrawFilledCircle(screen, c.Center.X, c.Center.Y, c.Radius, c.Color, true)
	}
	// vanished tagged lines
	for t := 0; t < MaxTags; t += 1 {
		col := TagColors[t]
		col.R >>= 1
		col.G >>= 1
		col.B >>= 1
		for p := 0; p < len(data.taggedVanishingPolylines[t])-1; p += 1 {
			drawPolyline(screen, data.taggedVanishingPolylines[t][p].Points, 1.0, col)
		}
	}
	// tagged polylines
	for t := 0; t < MaxTags; t += 1 {
		if len(data.taggedVanishingPolylines[t]) > 0 {
			col := TagColors[t]
			drawPolyline(screen, data.taggedVanishingPolylines[t][len(data.taggedVanishingPolylines[t])-1].Points, 2.0, col)
		}
	}
	// tagged texts
	for t := 0; t < MaxTags; t += 1 {
		if data.taggedTexts[t].Text != "" {

			vector.DrawFilledCircle(screen, 16, 14+float32(t*20), 8, TagColors[t], true)
			text.Draw(screen, data.taggedTexts[t].Text, &text.GoTextFace{
				Source: data.textFaceSource,
				Size:   20,
			}, data.taggedTexts[t].drawOptions)
		}
	}
}

func drawPolyline(screen *ebiten.Image, points []Point, strokeWidth float32, color color.RGBA) {
	xe := points[0].X
	ye := points[0].Y
	for i := 1; i < len(points); i += 1 {
		xs := xe
		ys := ye
		xe = points[i].X
		ye = points[i].Y
		vector.StrokeLine(screen, xs, ys, xe, ye, strokeWidth, color, true)
	}
}

func Run(feed <-chan interface{}, title string, playgroundSize, windowSize int) {
	var err error

	// setup window
	ebiten.SetWindowSize(windowSize, windowSize)
	ebiten.SetWindowTitle(title)

	// Call ebiten.RunGame to start your game loop.
	data := &vizData{feed: feed, playgroundSize: playgroundSize}
	if data.textFaceSource, err = text.NewGoTextFaceSource(bytes.NewReader(fonts.MPlus1pRegular_ttf)); err != nil {
		log.Fatal(err)
	}
	if err := ebiten.RunGame(data); err != nil {
		log.Fatal(err)
	}
}
