import { describe, it, expect, vi, afterEach } from 'vitest'
import { DownloadRoute } from '../../src/components/DownloadRoute'

describe('ST-08 Route Export', () => {
    afterEach(() => {
        vi.restoreAllMocks()
        vi.unstubAllGlobals()
    })
    it.each(['basic', 'optimized'])('exports %s route waypoints in RTZ format', async (routeType) => {
        const routePoints: [number, number][] = [
            [37.0, -7.0],
            [36.75, -6.75],
            [36.5, -6.5]
        ]

        const createObjectURLMock = vi.fn((_blob: Blob) => 'blob:test-url')

        const revokeObjectURLMock = vi.fn()

        vi.stubGlobal('URL', {
            createObjectURL: createObjectURLMock,
            revokeObjectURL: revokeObjectURLMock
        })

        const clickMock = vi.spyOn(
            HTMLAnchorElement.prototype,
            'click'
        ).mockImplementation(() => {})

        const result = DownloadRoute({ routePoints, routeType })

        expect(result).toBe('done')
        expect(createObjectURLMock).toHaveBeenCalledTimes(1)
        expect(clickMock).toHaveBeenCalledTimes(1)
        expect(revokeObjectURLMock).toHaveBeenCalledWith('blob:test-url')

        const blob = createObjectURLMock.mock.calls[0][0]

        expect(blob).toBeInstanceOf(Blob)
        expect(blob.type).toBe('application/xml;charset=utf-8;')

        const xml = await blob.text()

        console.log(xml)

        const parser = new DOMParser()
        const xmlDoc = parser.parseFromString(xml, 'application/xml')

        expect(xmlDoc.querySelector('parsererror')).toBeNull()
        expect(xmlDoc.documentElement.localName).toBe('route')
        expect(xmlDoc.documentElement.getAttribute('version')).toBe('1.2')
        expect(xmlDoc.documentElement.namespaceURI).toBe('http://cirm.org')

        const waypoints = xmlDoc.querySelectorAll('waypoint')
        expect(waypoints.length).toBe(routePoints.length)

        waypoints.forEach((waypoint, i) => {
            const position = waypoint.querySelector('position')

            expect(waypoint.getAttribute('id')).toBe(String(i))
            expect(position).not.toBeNull()

            expect(position?.getAttribute('lat')).toBe(
                routePoints[i][0].toFixed(6)
            )

            expect(position?.getAttribute('lon')).toBe(
                routePoints[i][1].toFixed(6)
            )
        })

        const routeInfo = xmlDoc.querySelector('routeInfo')

        expect(routeInfo).not.toBeNull()
        expect(routeInfo?.getAttribute('routeName')).toMatch(new RegExp(`^${routeType}Route_\\d{1,2}-\\d{1,2}-\\d{4}$`))

        const downloadLink = clickMock.mock.contexts[0] as HTMLAnchorElement

        expect(downloadLink.download).toMatch(new RegExp(`^${routeType}Route_\\d{1,2}-\\d{1,2}-\\d{4}\\.rtz$`))
        expect(downloadLink.href).toBe('blob:test-url')

        expect(downloadLink.download).toBe(`${routeInfo?.getAttribute('routeName')}.rtz`)

    })


    it('normalizes longitude values during RTZ export', async () => {
        const routePoints: [number, number][] = [
            [37.0, 190.0],
            [36.75, -190.0],
            [36.5, 180.0],
            [36.25, 360.0]
        ]

        const expectedLongitudes = [
            '-170.000000',
            '170.000000',
            '-180.000000',
            '0.000000'
        ]

        const routeType = 'optimized'

        const createObjectURLMock = vi.fn((_blob: Blob) => 'blob:test-url')

        const revokeObjectURLMock = vi.fn()

        vi.stubGlobal('URL', {
            createObjectURL: createObjectURLMock,
            revokeObjectURL: revokeObjectURLMock
        })

        const clickMock = vi.spyOn(
            HTMLAnchorElement.prototype,
            'click'
        ).mockImplementation(() => {})

        const result = DownloadRoute({ routePoints, routeType })

        expect(result).toBe('done')
        expect(createObjectURLMock).toHaveBeenCalledTimes(1)
        expect(clickMock).toHaveBeenCalledTimes(1)

        const blob = createObjectURLMock.mock.calls[0][0]

        const xml = await blob.text()

        console.log(xml)
        const parser = new DOMParser()
        const xmlDoc = parser.parseFromString(xml, 'application/xml')

        expect(xmlDoc.querySelector('parsererror')).toBeNull()

        const waypoints = xmlDoc.querySelectorAll('waypoint')
        expect(waypoints.length).toBe(routePoints.length)

        waypoints.forEach((waypoint, i) => {
            const position = waypoint.querySelector('position')

            expect(waypoint.getAttribute('id')).toBe(String(i))
            expect(position).not.toBeNull()

            expect(position?.getAttribute('lat')).toBe(
                routePoints[i][0].toFixed(6)
            )

            expect(position?.getAttribute('lon')).toBe(
                expectedLongitudes[i]
            )
        })


    })
})



