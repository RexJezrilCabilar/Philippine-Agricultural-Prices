import KPI from './KPI'


export default function Home({data}) {

    const prices = data.map(item => ({
        commodity: item.Commodity,
        price: Number(item.Price_PHP)
    }))

    const groupedPrices = Object.groupBy(prices, item => item.commodity);
    const averagePrices = Object.entries(groupedPrices).map(([commodity, items]) => {
        const total = items.reduce((sum, item) => sum + item.price, 0);
        const average = total / items.length;

        return {
            Commodity: commodity,
            Average_Price: average.toFixed(2)
        }

    });

    return(
        <div>
            <h2 >Price Data</h2>
            <KPI data={averagePrices} />
        </div>
    )

}
