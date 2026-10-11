type WeatherSliderProps = {
    overlayReady: boolean
    overlayDate: string | null
    overlayHours: number[] | null
    selectedOverlayHour: number 
    setSelectedOverlayHour: (hour: number) => void
}

function WeatherSlider({overlayReady, overlayDate, overlayHours, selectedOverlayHour, setSelectedOverlayHour}: WeatherSliderProps) {
    return (
        <div className="weather-slider-wrapper">
        {overlayReady && overlayHours && (
            <div className="weather-slider-container">
                <div className="weather-slider-info">
                <p>Forecast Date: {overlayDate}</p>
                <p>Overlay datetime: {overlayHours[selectedOverlayHour]}</p>
                </div>
                <div className="weather-slider-input">
                <input type="range" min={0} max={overlayHours.length - 1} value={selectedOverlayHour} onChange={(e) => setSelectedOverlayHour(parseInt(e.target.value))} />
                </div>
            </div>
        )}
        </div>
    )
}

export default WeatherSlider;