type LegendProps = {
    visible: boolean;
}

function Legend({visible}: LegendProps) {
    if (!visible) return null;

    return (
        <div className="wave-legend" aria-label="Significant wave height legend">
            <div className="wave-legend-title">Hs (m)</div>
                <div className="wave-legend-bar-wrap">
                    <span>10</span>
                        <div className="wave-legend-bar" />
                    <span>0</span>
            </div>
        </div>
    );
}

export default Legend;