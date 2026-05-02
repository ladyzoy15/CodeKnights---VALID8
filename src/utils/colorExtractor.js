/**
 * Extracts dominant colors from an image file using Canvas API
 */
export async function extractDominantColors(file, count = 2) {
  return new Promise((resolve, reject) => {
    if (!file) {
      return reject(new Error('No file provided'));
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Use a small size for performance
        canvas.width = 50;
        canvas.height = 50;
        ctx.drawImage(img, 0, 0, 50, 50);
        
        const imageData = ctx.getImageData(0, 0, 50, 50).data;
        const colorCounts = {};
        
        // Loop through pixels (step 4 for RGBA)
        for (let i = 0; i < imageData.length; i += 4) {
          const r = imageData[i];
          const g = imageData[i+1];
          const b = imageData[i+2];
          const a = imageData[i+3];
          
          // Skip transparent or near-white/near-black pixels if desired
          // For now, just skip transparent
          if (a < 128) continue; 
          
          // Quantize colors to group similar shades
          const rgb = `${Math.round(r/15)*15},${Math.round(g/15)*15},${Math.round(b/15)*15}`;
          colorCounts[rgb] = (colorCounts[rgb] || 0) + 1;
        }
        
        // Sort colors by frequency
        const sortedColors = Object.entries(colorCounts)
          .sort((a, b) => b[1] - a[1])
          .slice(0, count)
          .map(([rgb]) => {
            const [r, g, b] = rgb.split(',').map(Number);
            return rgbToHex(r, g, b);
          });
          
        resolve(sortedColors);
      };
      img.onerror = () => reject(new Error('Failed to load image'));
      img.src = e.target.result;
    };
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsDataURL(file);
  });
}

function rgbToHex(r, g, b) {
  const componentToHex = (c) => {
    const hex = c.toString(16);
    return hex.length === 1 ? "0" + hex : hex;
  };
  return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}
