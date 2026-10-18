export default function KPI({data}) {

    return (
        <div className="flex flex-wrap gap-4 w-full max-w-4xl">
            {data.map((commodity) => (
                <div className="flex-1 min-w-[200px] border border-gray-300 rounded-lg p-4">
                    <p className="font-bold">{commodity.Commodity}</p>
                    <p className="text-gray-600">Average Price: {commodity.Average_Price}</p>
                </div>
            ))}
                
        </div>
    )



}