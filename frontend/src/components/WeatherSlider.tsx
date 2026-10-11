type WeatherSliderProps = {
    overlayReady: boolean
    overlayDate: string | null
    overlayHours: number[] | null
    selectedOverlayHour: number | null
    setSelectedOverlayHour: (hour: number) => void
}

function WeatherSlider({overlayReady, overlayDate, overlayHours}: WeatherSliderProps) {
    return (
        <div>
            <p>Weather Slider</p>
        {overlayReady && overlayHours && (
            <div>
                <p>Overlay Date: {overlayDate}</p>
                <p>Overlay Hours: {overlayHours.join(', ')}</p>
            </div>
        )}
        </div>
    )
}

export default WeatherSlider;