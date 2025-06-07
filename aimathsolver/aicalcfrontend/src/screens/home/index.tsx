
import { ColorSwatch, Group } from '@mantine/core';
import { Button } from '@/components/ui/button';
import { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import Draggable from 'react-draggable';
import { SWATCHES } from '@/constants';

interface GeneratedResult {
    expression: string;
    answer: string;
}

interface Response {
    expr: string;
    result: string;
    assign: boolean;
}

const neonButtonStyles = {
    backgroundColor: 'black',
    color: 'white',
    transition: '0.3s ease',
    boxShadow: '0 0 5px rgba(255, 255, 255, 0.5)',
};

const neonButtonHoverStyles = {
    boxShadow: '0 0 20px #00ff00, 0 0 30px #00ff00, 0 0 40px #00ff00, 0 0 50px #00ff00',
};

export default function Home() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [isDrawing, setIsDrawing] = useState(false);
    const [color, setColor] = useState('rgb(255, 255, 255)');
    const [reset, setReset] = useState(false);
    const [dictOfVars, setDictOfVars] = useState({});
    const [result, setResult] = useState<GeneratedResult>();
    const [latexPosition, setLatexPosition] = useState({ x: 10, y: 200 });
    const [latexExpression, setLatexExpression] = useState<Array<string>>([]);
    const [eraserSize, setEraserSize] = useState(10);
    const [isErasing, setIsErasing] = useState(false);

    useEffect(() => {
        if (latexExpression.length > 0 && window.MathJax) {
            setTimeout(() => {
                window.MathJax.Hub.Queue(['Typeset', window.MathJax.Hub]);
            }, 0);
        }
    }, [latexExpression]);

    useEffect(() => {
        if (result) {
            renderLatexToCanvas(result.expression, result.answer);
        }
    }, [result]);

    useEffect(() => {
        if (reset) {
            resetCanvas();
            setLatexExpression([]);
            setResult(undefined);
            setDictOfVars({});
            setReset(false);
        }
    }, [reset]);

    useEffect(() => {
        const canvas = canvasRef.current;

        if (canvas) {
            const ctx = canvas.getContext('2d');
            if (ctx) {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight - canvas.offsetTop;
                ctx.lineCap = 'round';
                ctx.lineWidth = 3;
            }
        }
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.9/MathJax.js?config=TeX-MML-AM_CHTML';
        script.async = true;
        document.head.appendChild(script);

        script.onload = () => {
            window.MathJax.Hub.Config({
                tex2jax: { inlineMath: [['$', '$'], ['\\(', '\\)']] },
            });
        };

        return () => {
            document.head.removeChild(script);
        };
    }, []);

    const renderLatexToCanvas = (expression: string, answer: string) => {
        const latex = `\\(\\LARGE{${expression} = ${answer}}\\)`;
        setLatexExpression([...latexExpression, latex]);

        const canvas = canvasRef.current;
        if (canvas) {
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
        }
    };

    const resetCanvas = () => {
        const canvas = canvasRef.current;
        if (canvas) {
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
        }
    };

    const startDrawing = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
        const canvas = canvasRef.current;
        if (canvas) {
            const ctx = canvas.getContext('2d');
            if (ctx) {
                let offsetX: number, offsetY: number;
                if ('touches' in e) {
                    offsetX = e.touches[0].clientX - canvas.offsetLeft;
                    offsetY = e.touches[0].clientY - canvas.offsetTop;
                } else {
                    offsetX = e.nativeEvent.offsetX;
                    offsetY = e.nativeEvent.offsetY;
                }
                ctx.beginPath();
                ctx.moveTo(offsetX, offsetY);
                setIsDrawing(true);
            }
        }
    };

    const draw = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
        if (!isDrawing) {
            return;
        }
        const canvas = canvasRef.current;
        if (canvas) {
            const ctx = canvas.getContext('2d');
            if (ctx) {
                let offsetX: number, offsetY: number;
                if ('touches' in e) {
                    offsetX = e.touches[0].clientX - canvas.offsetLeft;
                    offsetY = e.touches[0].clientY - canvas.offsetTop;
                } else {
                    offsetX = e.nativeEvent.offsetX;
                    offsetY = e.nativeEvent.offsetY;
                }
                if (isErasing) {
                    ctx.globalCompositeOperation = 'destination-out'; // Erase mode
                    ctx.lineWidth = eraserSize; // Use eraser size for erasing
                } else {
                    ctx.globalCompositeOperation = 'source-over'; // Drawing mode
                    ctx.strokeStyle = color;
                    ctx.lineWidth = eraserSize; // Use eraser size for drawing
                }
                ctx.lineTo(offsetX, offsetY);
                ctx.stroke();
            }
        }
    };

    const stopDrawing = () => {
        setIsDrawing(false);
    };

    const runRoute = async () => {
        const canvas = canvasRef.current;

        if (canvas) {
            const response = await axios({
                method: 'post',
                url: `${import.meta.env.VITE_API_URL}/calculate`,
                data: {
                    image: canvas.toDataURL('image/png'),
                    dict_of_vars: dictOfVars,
                },
            });

            const resp = await response.data;
            console.log('Response', resp);
            resp.data.forEach((data: Response) => {
                if (data.assign === true) {
                    setDictOfVars({
                        ...dictOfVars,
                        [data.expr]: data.result,
                    });
                }
            });
            const ctx = canvas.getContext('2d');
            const imageData = ctx!.getImageData(0, 0, canvas.width, canvas.height);
            let minX = canvas.width,
                minY = canvas.height,
                maxX = 0,
                maxY = 0;

            for (let y = 0; y < canvas.height; y++) {
                for (let x = 0; x < canvas.width; x++) {
                    const i = (y * canvas.width + x) * 4;
                    if (imageData.data[i + 3] > 0) {
                        minX = Math.min(minX, x);
                        minY = Math.min(minY, y);
                        maxX = Math.max(maxX, x);
                        maxY = Math.max(maxY, y);
                    }
                }
            }

            const centerX = (minX + maxX) / 2;
            const centerY = (minY + maxY) / 2;

            setLatexPosition({ x: centerX, y: centerY });
            resp.data.forEach((data: Response) => {
                setTimeout(() => {
                    setResult({
                        expression: data.expr,
                        answer: data.result,
                    });
                }, 1000);
            });
        }
    };

    useEffect(() => {
        const canvasElement = canvasRef.current;

        const preventTouchMove = (e: TouchEvent) => {
            // Prevent the default touchmove behavior (scrolling)
            e.preventDefault();
        };

        const preventTouchStart = (e: TouchEvent) => {
            // Prevent the default touchstart behavior (zoom or scroll)
            e.preventDefault();
        };

        if (canvasElement) {
            canvasElement.addEventListener('touchstart', preventTouchStart, { passive: false });
            canvasElement.addEventListener('touchmove', preventTouchMove, { passive: false });
        }

        return () => {
            if (canvasElement) {
                canvasElement.removeEventListener('touchstart', preventTouchStart);
                canvasElement.removeEventListener('touchmove', preventTouchMove);
            }
        };
    }, []);

    return (
        <>
            <div className="grid grid-cols-3 gap-2">
                <Button
                    onClick={() => setReset(true)}
                    className="z-20 bg-black text-white"
                    variant="default"
                    color="black"
                    style={neonButtonStyles}
                    onMouseEnter={(e) => (e.currentTarget.style.boxShadow = neonButtonHoverStyles.boxShadow)}
                    onMouseLeave={(e) => (e.currentTarget.style.boxShadow = neonButtonStyles.boxShadow)}
                >
                    Reset
                </Button>
                <Group className="z-20">
                    {SWATCHES.map((swatch) => (
                        <ColorSwatch key={swatch} color={swatch} onClick={() => setColor(swatch)} />
                    ))}
                </Group>
                <Button
                    onClick={runRoute}
                    className="z-20 bg-black text-white"
                    variant="default"
                    color="white"
                    style={neonButtonStyles}
                    onMouseEnter={(e) => (e.currentTarget.style.boxShadow = neonButtonHoverStyles.boxShadow)}
                    onMouseLeave={(e) => (e.currentTarget.style.boxShadow = neonButtonStyles.boxShadow)}
                >
                    Run
                </Button>
                <Button
                    onClick={() => setIsErasing(!isErasing)}
                    className="z-20 bg-black text-white"
                    variant="default"
                    color="white"
                    style={neonButtonStyles}
                    onMouseEnter={(e) => (e.currentTarget.style.boxShadow = neonButtonHoverStyles.boxShadow)}
                    onMouseLeave={(e) => (e.currentTarget.style.boxShadow = neonButtonStyles.boxShadow)}
                >
                    {isErasing ? 'Switch to Draw' : 'Switch to Erase'}
                </Button>
                <input
                    type="range"
                    min="1"
                    max="50"
                    value={eraserSize}
                    onChange={(e) => setEraserSize(Number(e.target.value))}
                    className="z-20"
                />
            </div>
            <canvas
                ref={canvasRef}
                id="canvas"
                className="absolute top-0 left-0 w-full h-full"
                style={{
                    position: 'fixed', // Fix the canvas position
                    top: 0,
                    left: 0,
                }}
                onMouseDown={startDrawing}
                onMouseMove={draw}
                onMouseUp={stopDrawing}
                onMouseOut={stopDrawing}
                onTouchStart={startDrawing}
                onTouchMove={draw}
                onTouchEnd={stopDrawing}
            />

            {latexExpression && latexExpression.map((latex, index) => (
                <Draggable
                    key={index}
                    defaultPosition={latexPosition}
                    onStop={(_, data) => setLatexPosition({ x: data.x, y: data.y })}
                >
                    <div className="absolute p-2 text-black rounded shadow-md">
                        <div className="latex-content">{latex}</div>
                    </div>
                </Draggable>
            ))}
        </>
    );
}
