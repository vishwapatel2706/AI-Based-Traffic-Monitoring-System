## Frontend - React App

This is the web interface for the Traffic Vehicle Classifier system.

### Prerequisites

- Node.js 14+ (includes npm)
- Backend server running on `http://localhost:5000`

### Setup Instructions

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm start
   ```

   The app will automatically open at `http://localhost:3000`

3. **Build for production:**
   ```bash
   npm run build
   ```

   This creates an optimized production build in the `build/` folder.

### Features

- 📸 **Image Upload**: Drag-and-drop or click to upload vehicle images
- 🔗 **URL Input**: Analyze images directly from URLs
- 🎯 **Real-time Predictions**: Instant vehicle classification
- 📊 **Confidence Scores**: View prediction confidence for all classes
- ⚠️ **Priority Indicators**: Emergency vehicle detection with priority levels
- 🎨 **Beautiful UI**: Modern, responsive interface

### How to Use

1. **Start the backend server** (see backend README)
2. **Start the frontend app** (`npm start`)
3. **Upload an image:**
   - Drag and drop a vehicle image onto the upload area, OR
   - Click to select a file, OR
   - Switch to "From URL" tab and paste an image URL
4. **View results:**
   - See predicted vehicle type
   - Check confidence percentage
   - View priority level for emergency vehicles
   - See probabilities for all possible classes

### Project Structure

```
frontend/
├── public/
│   └── index.html              # Main HTML file
├── src/
│   ├── components/
│   │   ├── ImageUploader.js     # File/URL upload component
│   │   ├── ImageUploader.css
│   │   ├── PredictionResult.js  # Results display component
│   │   ├── PredictionResult.css
│   │   ├── ClassesList.js       # Available classes component
│   │   └── ClassesList.css
│   ├── App.js                   # Main app component
│   ├── App.css
│   ├── index.js                 # React entry point
│   └── index.css                # Global styles
├── package.json
└── README.md
```

### API Connection

The frontend connects to the backend at `http://localhost:5000/api`

If you want to use a different backend URL, edit `App.js`:

```javascript
const API_URL = 'http://your-backend-url:5000/api';
```

### Supported Image Formats

- JPG / JPEG
- PNG
- GIF

Maximum recommended image size: 10 MB

### Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### Troubleshooting

1. **"API Offline" message:**
   - Make sure backend server is running on `http://localhost:5000`
   - Check that `app.py` is executed without errors

2. **Port 3000 already in use:**
   ```bash
   # Use a different port
   PORT=3001 npm start
   ```

3. **Images not uploading:**
   - Check browser console for errors (F12)
   - Ensure backend is running and accessible
   - Verify CORS is enabled in backend

4. **Slow predictions:**
   - This is normal for the first prediction (model loading)
   - Subsequent predictions are faster (cached in GPU/CPU)

### Development Commands

```bash
npm start         # Start dev server (port 3000)
npm run build     # Build for production
npm test          # Run tests (if configured)
npm run eject     # Expose webpack config (⚠️ irreversible)
```

### Tips

- The model is optimized for 96x96 images but accepts any size
- Clearer, well-lit images produce better predictions
- Multiple vehicles in frame: model predicts the most prominent one
- Use the URL tab to test with external images without uploading

### Environment Variables

Create a `.env` file in the frontend folder to customize:

```
REACT_APP_API_URL=http://localhost:5000/api
```

Then update `App.js` to use: `process.env.REACT_APP_API_URL`

