﻿using NNSharp.DataTypes;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using static NNSharp.DataTypes.Data2D;

namespace NNSharp.Kernels.CPUKernels
{
    [Serializable()]
    public class GlobalAvgPool2DKernel : IKernel
    {
        public void Execute()
        {
            Dimension dimI = input.GetDimension();

            for (int batch = 0; batch < dimI.b; ++batch)
            {
                for (int channel = 0; channel < dimI.c; ++channel)
                {
                    double sum = 0.0;
                    for (int h = 0; h < dimI.h; ++h)
                    {
                        for (int w = 0; w < dimI.w; ++w)
                        {
                            sum += input[h, w, channel, batch];
                        }
                    }

                    output[0, 0, channel, batch] = sum / (dimI.h * dimI.w);
                }
            }
        }

        protected Data2D input;
        protected Data2D output;
    }
}
