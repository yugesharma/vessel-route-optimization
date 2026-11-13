type DownloadRouteProps={
    routePoints: [number, number][]
    routeType: string
}

export function DownloadRoute({routePoints,routeType}:DownloadRouteProps) {
    const waypoints=routePoints.map((wp,i)=>{
        return `<waypoint id="${i}"> <position lat ="${wp[0].toFixed(6)}" lon ="${wp[1].toFixed(6)}" />
        </waypoint>`;
    }).join('\n');
    const date = new Date();

    let day = date.getDate();
    let month = date.getMonth() + 1;
    let year = date.getFullYear();

    let currentDate = `${day}-${month}-${year}`;

    const routeXml= `<?xml version="1.0" encoding="UTF-8"?>
            <route xmlns="http://cirm.org" version="1.2">
            <routeInfo routeName="${routeType}Route_${currentDate}"/>
            <waypoints>
            ${waypoints}
            </waypoints>
            </route>`;
    
    const blob=new Blob([routeXml],{type:'application/xml;charset=utf-8;'})
    const url=URL.createObjectURL(blob);

    const link=document.createElement('a')
    link.href=url
    link.download=`${routeType}Route_${currentDate}.rtz`
    link.click()
    URL.revokeObjectURL(url)

    return 'done'
}