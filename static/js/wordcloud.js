// Mentimeter-style Live Word Cloud Canvas Renderer
class WordCloudRenderer {
  constructor(canvasElement) {
    this.canvas = canvasElement;
    this.ctx = canvasElement ? canvasElement.getContext('2d') : null;
    this.colors = ['#38bdf8', '#818cf8', '#c084fc', '#f472b6', '#fb7185', '#34d399', '#fbbf24'];
  }

  setCanvas(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
  }

  render(wordTally) {
    if (!this.canvas || !this.ctx) return;
    const ctx = this.ctx;
    const width = this.canvas.width;
    const height = this.canvas.height;

    ctx.clearRect(0, 0, width, height);

    const words = Object.entries(wordTally);
    if (words.length === 0) {
      ctx.fillStyle = '#64748b';
      ctx.font = '20px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('Menunggu respons kata dari peserta...', width / 2, height / 2);
      return;
    }

    // Sort words by count descending
    words.sort((a, b) => b[1] - a[1]);
    const maxCount = words[0][1];
    const minCount = words[words.length - 1][1];

    const centerX = width / 2;
    const centerY = height / 2;

    // Spiral placement algorithm
    const placedBoxes = [];

    words.forEach(([word, count], index) => {
      // Calculate font size (min 20px, max 64px)
      let fontSize = 24;
      if (maxCount > minCount) {
        fontSize = 22 + Math.round(((count - minCount) / (maxCount - minCount)) * 42);
      } else {
        fontSize = 32;
      }

      ctx.font = `bold ${fontSize}px sans-serif`;
      const textMetrics = ctx.measureText(word);
      const textWidth = textMetrics.width;
      const textHeight = fontSize * 1.1;

      // Find non-overlapping position using Archimedean spiral
      let angle = index * 2.4;
      let radius = 10;
      let placed = false;
      let posX = centerX;
      let posY = centerY;

      for (let step = 0; step < 120; step++) {
        const testX = centerX + radius * Math.cos(angle);
        const testY = centerY + radius * Math.sin(angle);

        const box = {
          left: testX - textWidth / 2 - 8,
          right: testX + textWidth / 2 + 8,
          top: testY - textHeight / 2 - 4,
          bottom: testY + textHeight / 2 + 4
        };

        // Check if within bounds
        if (box.left < 10 || box.right > width - 10 || box.top < 10 || box.bottom > height - 10) {
          radius += 5;
          angle += 0.3;
          continue;
        }

        // Check collision with previously placed words
        let collision = false;
        for (const p of placedBoxes) {
          if (!(box.left > p.right || box.right < p.left || box.top > p.bottom || box.bottom < p.top)) {
            collision = true;
            break;
          }
        }

        if (!collision) {
          posX = testX;
          posY = testY;
          placedBoxes.push(box);
          placed = true;
          break;
        }

        radius += 4;
        angle += 0.35;
      }

      // Draw word
      const color = this.colors[index % this.colors.length];
      ctx.save();
      ctx.font = `800 ${fontSize}px sans-serif`;
      ctx.fillStyle = color;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.shadowColor = 'rgba(0, 0, 0, 0.4)';
      ctx.shadowBlur = 6;
      ctx.shadowOffsetY = 2;
      ctx.fillText(word, posX, posY);
      ctx.restore();
    });
  }
}
